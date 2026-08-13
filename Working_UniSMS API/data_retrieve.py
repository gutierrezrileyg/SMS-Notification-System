import io
import site
import sqlite3
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

@dataclass
class ResidentProfile:
    resident_id: Optional[int] = None
    full_name: str = "Unknown"
    age: Optional[int] = None
    phone_number: str = ""
    email: Optional[str] = None
    barangay: str = ""
    city: str = "Lipa City"
    province: str = "Batangas"
    address_line: Optional[str] = None

class ResidentDatabase:
    def __init__(self, db_name: str = ":memory:"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        schema = """
        CREATE TABLE IF NOT EXISTS resident_profiles (
            resident_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER,
            phone_number TEXT NOT NULL,
            email TEXT,
            barangay TEXT NOT NULL,
            city TEXT NOT NULL,
            province TEXT NOT NULL,
            address_line TEXT,
            UNIQUE(phone_number, barangay)
        );
        """
        with self.conn:
            self.conn.execute(schema)

    def insert_profile(self, profile: ResidentProfile) -> bool:
        query = """
        INSERT OR IGNORE INTO resident_profiles
        (full_name, age, phone_number, email, barangay, city, province, address_line)
        VALUES (:full_name, :age, :phone_number, :email, :barangay, :city, :province, :address_line);
        """
        with self.conn:
            cursor = self.conn.execute(query, asdict(profile))
            return cursor.rowcount > 0

    def get_profiles_by_barangay(self, barangay_name: str) -> List[ResidentProfile]:
        query = """
        SELECT resident_id, full_name, age, phone_number, email, barangay, city, province, address_line
        FROM resident_profiles
        WHERE LOWER(barangay) = LOWER(?);
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (barangay_name.strip(),))
        rows = cursor.fetchall()

        return [
            ResidentProfile(
                resident_id=row[0],
                full_name=row[1],
                age=row[2],
                phone_number=row[3],
                email=row[4],
                barangay=row[5],
                city=row[6],
                province=row[7],
                address_line=row[8],
            )
            for row in rows
        ]

class ResidentDataFetcher:
    def __init__(self, excel_url_or_path: str = "Testing Interface (1).xlsx"):
        self.source = excel_url_or_path
        self.df = self._load_dataframe(excel_url_or_path)
        self._standardize_columns()

    def _load_dataframe(self, path_or_url: str) -> pd.DataFrame:
        try:
            if path_or_url.endswith(".xlsx") or path_or_url.endswith(".xls"):
                df = pd.read_excel(
                    path_or_url,
                    sheet_name="Database",
                    header=2,
                    engine="openpyxl",
                )
            else:
                df = pd.read_csv(path_or_url, header=2)

            if "Barangay" in df.columns:
                df["Barangay"] = df["Barangay"].ffill()

            return df
        except FileNotFoundError:
            print(f"[File Error] Could not find spreadsheet at: {path_or_url}")
            return pd.DataFrame()
        except Exception as e:
            print(f"[System Error] Failed to read spreadsheet: {e}")
            return pd.DataFrame()

    def _standardize_columns(self):
        if self.df.empty:
            return

        col_mapping = {}
        for col in self.df.columns:
            clean_col = str(col).strip().lower().replace("_", " ")
            if "name" in clean_col:
                col_mapping[col] = "Full_Name"
            elif "age" in clean_col:
                col_mapping[col] = "Age"
            elif any(term in clean_col for term in ["phone", "mobile", "contact", "cellphone"]):
                col_mapping[col] = "Phone_Number"
            elif "email" in clean_col:
                col_mapping[col] = "Email"
            elif "barangay" in clean_col:
                col_mapping[col] = "Barangay"
            elif "address" in clean_col or "street" in clean_col:
                col_mapping[col] = "Address_Line"

        self.df.rename(columns=col_mapping, inplace=True)

    def extract_raw_profiles(self) -> List[Dict[str, Any]]:
        if self.df.empty:
            return []
        return self.df.to_dict(orient="records")

def validate_phone(phone: Any) -> bool:
    if pd.isna(phone) or not phone:
        return False
    return len(str(phone).strip()) > 0

def sanitize_profile(raw_record: Dict[str, Any]) -> Optional[ResidentProfile]:
    raw_phone = raw_record.get("Phone_Number")
    if not validate_phone(raw_phone):
        return None

    phone_number = str(raw_phone).strip()
    raw_age = raw_record.get("Age")
    try:
        age = int(raw_age) if pd.notna(raw_age) else None
    except (ValueError, TypeError):
        age = None

    raw_barangay = str(raw_record.get("Barangay", "")).strip()

    return ResidentProfile(
        full_name=str(raw_record.get("Full_Name", "Unknown Resident")).strip(),
        age=age,
        phone_number=phone_number,
        email=str(raw_record.get("Email")).strip() if pd.notna(raw_record.get("Email")) else None,
        barangay=raw_barangay,
        address_line=str(raw_record.get("Address_Line")).strip() if pd.notna(raw_record.get("Address_Line")) else None,
    )

def routing_logic(barangay_name: str, profiles: List[ResidentProfile]) -> Dict[str, Any]:
    phone_list = [p.phone_number for p in profiles]
    return {
        "destination": "GatewayAPI",
        "barangay": barangay_name,
        "queue_name": f"SMS_QUEUE_{barangay_name.upper().replace(' ', '_')}",
        "total_messages": len(phone_list),
        "payload": phone_list,
        "profiles_count": len(profiles),
    }

def gateway_api(route_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Message Queue] Enqueued {route_data['total_messages']} numbers for '{route_data['barangay']}' -> {route_data['queue_name']}")
    return {
        "status": "ready",
        "barangay": route_data["barangay"],
        "records": route_data["payload"],
    }
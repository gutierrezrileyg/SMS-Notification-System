import os
import time
import requests
from requests.auth import HTTPBasicAuth

# Imported all necessary classes and helpers, including ExcelStatusUpdater
from data_retrieve import (
    ResidentDatabase,
    ResidentDataFetcher,
    sanitize_profile,
    routing_logic,
    gateway_api,
    ExcelStatusUpdater,  # <--- Added ExcelStatusUpdater here
)


def main():
    print("==================================================")
    print("    CENRO SMS NOTIFICATION ORCHESTRATOR           ")
    print("==================================================")

    start_input = input("Enter 'Start' to begin the system flow: ").strip()
    if start_input.lower() != "start":
        print("[Abort] Invalid entry. Exiting flow.")
        return

    print("\nAvailable Barangays:")
    print("  [1] Poblacion 1")
    print("  [2] Poblacion 2")
    print("  [3] Poblacion 3")
    print("  [4] Poblacion 4")

    choice = input("\nSelect barangay (Enter name or number 1-4): ").strip()

    barangay_map = {
        "1": "Poblacion 1",
        "2": "Poblacion 2",
        "3": "Poblacion 3",
        "4": "Poblacion 4",
    }

    selected_barangay = barangay_map.get(choice, choice)
    valid_barangays = ["Poblacion 1", "Poblacion 2", "Poblacion 3", "Poblacion 4"]
    if selected_barangay not in valid_barangays:
        print(f"[Error] '{selected_barangay}' is not a valid target barangay.")
        return

    print(f"\n[Selected] Target Barangay set to: {selected_barangay}")

    print("\n[Step 3] Initializing Database & Fetching Spreadsheet Data...")
    db = ResidentDatabase()

    # Use your absolute file path consistently
    file_path = r"C:\Users\Riley G. Gutierrez\OneDrive\Documents\My Codes\unisms-sender\Testing Interface (1).xlsx"
    fetcher = ResidentDataFetcher(file_path)

    raw_records = fetcher.extract_raw_profiles()

    for record in raw_records:
        profile = sanitize_profile(record)
        if profile and profile.barangay:
            db.insert_profile(profile)

    profiles_list = db.get_profiles_by_barangay(selected_barangay)

    if not profiles_list:
        print(f"[Warning] No resident profiles found for {selected_barangay}.")
        return

    print(f"[Step 4] Formatted phone numbers ready for dispatch: {[p.phone_number for p in profiles_list]}")

    print(
        f"\n[Step 5] Beginning sequential SMS broadcast loop for {selected_barangay}..."
    )

    sms_api_url = "https://unismsapi.com/api/sms"
    api_secret_key = "sk_0CTaxWySoUjATZr0-6QdKU7dVFOxueqDJZiXo4ilN3rs4nrktVOgPjEQoBpjUHCo32Hi87DbebbAyGYaDWgTdQ-1759"

    message_content = (
        "Trash Collector is approaching your area. Please prepare your segregated waste."
    )

    # Dictionary to track the delivery status of each phone number
    latest_statuses = {}

    for index, profile in enumerate(profiles_list, start=1):
        phone = profile.phone_number
        payload = {
            "recipient": phone,
            "content": message_content,
            "sender_id": "Unisoft",
            "metadata": {
                "order_id": f"1234{index}",
                "template": "order_confirmation",
            },
        }

        headers = {
            "Content-Type": "application/json",
        }

        print(
            f" -> Sending message {index} of {len(profiles_list)} to phone:"
            f" {phone}..."
        )
        try:
            response = requests.post(
                sms_api_url,
                json=payload,
                auth=HTTPBasicAuth(api_secret_key, ""),
                headers=headers,
                timeout=10,
            )
            print(f"    Response: {response.status_code} - {response.text}")
            
            # Check if the API request was successful and update status accordingly
            if response.status_code in [200, 201]:
                latest_statuses[phone] = "Sent"
            else:
                latest_statuses[phone] = f"Failed ({response.status_code})"
                
        except Exception as e:
            print(f"    [API Error] Failed to send to {phone}: {e}")
            latest_statuses[phone] = "Failed"

        time.sleep(1)

    print(
        "\n[Step 6] Triggering routing queue and ensuring webhook synchronization..."
    )
    route_data = routing_logic(selected_barangay, profiles_list)
    gateway_api(route_data)

    print(
        "[Step 7] Processing status overwrites and writing back to Excel file..."
    )
    
    # Write the collected live statuses directly back into your Excel file
    if latest_statuses:
        excel_updater = ExcelStatusUpdater(excel_path=file_path)
        excel_updater.update_statuses(latest_statuses)

    time.sleep(1.5)

    print("\n==================================================")
    print(" Sending Completed, It is ready again for testing.")
    print("==================================================")


if __name__ == "__main__":
    main()
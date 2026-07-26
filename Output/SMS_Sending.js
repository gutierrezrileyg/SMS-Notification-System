const axios = require('axios');
const { execSync } = require('child_process');

function getSanitizedSMSMessage() {
  try {
    const output = execSync('python script.py', { encoding: 'utf-8' });
    return output.trim();
  } catch (error) {
    console.error("Failed to generate SMS via Python validation:", error.message);
    process.exit(1);
  }
}

function getDynamicRecipients() {
  try {
    // Executes your recipient-fetching Python script
    const output = execSync('python get_recipients.py', { encoding: 'utf-8' });
    
    // Parse the JSON string output from Python into a real JavaScript array
    return JSON.parse(output.trim());
  } catch (error) {
    console.error("Failed to fetch recipients from Python:", error.message);
    process.exit(1);
  }
}

async function sendSMS() {
  // Automatically pull the dynamic message and recipients from Python
  const finalMessage = getSanitizedSMSMessage();
  const dynamicRecipients = getDynamicRecipients();

  try {
    const response = await axios.post('https://unismsapi.com/api/sms', {
      recipients: dynamicRecipients, // Injects the Python-collected numbers here!
      content: finalMessage,         // Injects the Python-validated message here!
      sender_id: 'CENRO',
      metadata: {
        campaign: 'spring_sale_2026',
        template: 'order_confirmation'
      }
    }, {
      auth: {
        username: 'YOUR_SECRET_KEY',
        password: ''
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log("SMS Sent Successfully:", response.data);
  } catch (error) {
    console.error("API Request Failed:", error.response?.data || error.message);
  }
}

sendSMS();
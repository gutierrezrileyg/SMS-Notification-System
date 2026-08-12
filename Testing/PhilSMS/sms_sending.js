const axios = require('axios');

async function sendSms() {
  try {
    const response = await axios.post('https://unismsapi.com/api/blast', {
      recipients: [
        "+639606928499",
        "+639483449806",
        "+639924236075"
      ],
      content: 
        "Garbage truck is approaching your area. Please prepare your segregated waste.",
      sender_id: 'Unisoft',
      metadata: {
        order_id: '12345',
        template: 'order_confirmation'
      }
    }, {
      auth: {
        username: 'sk__9lLevZsmYGbjuQ-76HRgBBQLPoOgS97AfeleU2xf_qk-hcY9T1ND069ZOtllOzsH8J78t6sUzcFxHNL4AbMjA-1646',
        password: ''
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log(response.data);
  } catch (error) {
    console.error('Error sending SMS:', error.response ? error.response.data : error.message);
  }
}

sendSms();
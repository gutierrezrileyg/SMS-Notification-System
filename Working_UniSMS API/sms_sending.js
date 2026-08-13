const axios = require('axios');

async function sendSms() {
  try {
    const response = await axios.post('https://unismsapi.com/api/sms', {
      recipients: [phone_number], // Replace with the actual phone number],
      content: "This message was sent succesfully. Congratulations!!!",
      sender_id: 'Unisoft',
      metadata: {
        order_id: '12345',
        template: 'order_confirmation'
      }
    }, {
      auth: {
        username: 'sk_0CTaxWySoUjATZr0-6QdKU7dVFOxueqDJZiXo4ilN3rs4nrktVOgPjEQoBpjUHCo32Hi87DbebbAyGYaDWgTdQ-1759', // Replace with your actual API key
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
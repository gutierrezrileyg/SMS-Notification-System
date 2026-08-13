const axios = require('axios');

async function sendSms() {
  try {
    const response = await axios.post('https://unismsapi.com/api/blast', {
      recipients: [phone_number], // Replace with the actual phone number],
      content: "Hello, magkano po 50 kilo ng bigas? Salamat po.",
      sender_id: 'Unisoft',
      metadata: {
        order_id: '12345',
        template: 'order_confirmation'
      }
    }, {
      auth: {
        username: 'sk_hZQrBzBd9HPv7jQ8r_UkGnuEOa6uXNDndrn7TL-SqzaW5Ftc5lCSeEQudHUWqn-b0Xd4nAb3ScBycothwz4j1A-1646',
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
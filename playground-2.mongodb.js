
const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');

const app = express();
app.use(cors());
app.use(express.json());

const uri = "<YOUR_MONGODB_CONNECTION_STRING>";
const client = new MongoClient(uri);

app.post('/chat', async (req, res) => {
  const userMessage = req.body.message || "";

  // Assuming you have a collection to store chat messages
  const db = client.db('<YOUR_DATABASE_NAME>');
  const collection = db.collection('<YOUR_COLLECTION_NAME>');

  try {
    console.log('Inserting message into database...');
    const response = await collection.insertOne({ message: userMessage });
    console.log('Message inserted successfully:', response.insertedId);
    res.json({ reply: "Message stored successfully", id: response.insertedId });
  } catch (error) {
    console.error('Error inserting message:', error);
    res.status(500).json({ reply: "Sorry, I couldn't process that." });
  }
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
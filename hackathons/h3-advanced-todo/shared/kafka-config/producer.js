// shared/kafka-config/producer.js
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'h3-advanced-todo',
  brokers: [process.env.KAFKA_BROKER || 'localhost:9092']
});

const producer = kafka.producer();

module.exports = { producer };
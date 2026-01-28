// shared/kafka-config/consumer.js
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'h3-advanced-todo',
  brokers: [process.env.KAFKA_BROKER || 'localhost:9092']
});

const consumer = kafka.consumer({ groupId: 'h3-consumer-group' });

module.exports = { consumer };
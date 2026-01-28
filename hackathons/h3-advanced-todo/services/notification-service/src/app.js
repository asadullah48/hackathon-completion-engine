// services/notification-service/src/app.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { consumer } = require('../../shared/kafka-config/consumer');
const { TaskCreatedEventSchema, TaskAssignedEventSchema, DeadlineApproachingEventSchema } = require('../../shared/schemas/eventSchemas');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Mock notification storage (in production, use MongoDB)
let notifications = [];

// Email service mock (in production, use nodemailer with real email service)
const sendEmail = async (to, subject, body) => {
  console.log(`EMAIL SENT to ${to}: ${subject}\n${body}`);
  // In production: implement actual email sending
};

// SMS service mock (in production, use Twilio or similar)
const sendSMS = async (to, message) => {
  console.log(`SMS SENT to ${to}: ${message}`);
  // In production: implement actual SMS sending
};

// Push notification service mock
const sendPushNotification = async (userId, title, body) => {
  console.log(`PUSH NOTIFICATION to ${userId}: ${title}\n${body}`);
  // In production: implement actual push notification service
};

// Connect to Kafka consumer
async function connectConsumer() {
  await consumer.connect();
  console.log('Kafka consumer connected');
  
  // Subscribe to task events
  await consumer.subscribe({ topic: 'task-events', fromBeginning: true });
  
  // Process messages
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      try {
        const eventData = JSON.parse(message.value.toString());
        
        // Route events to appropriate handlers
        switch (eventData.eventType) {
          case 'TaskCreated':
            await handleTaskCreated(eventData);
            break;
          case 'TaskAssigned':
            await handleTaskAssigned(eventData);
            break;
          case 'DeadlineApproaching':
            await handleDeadlineApproaching(eventData);
            break;
          default:
            console.log(`Unknown event type: ${eventData.eventType}`);
        }
      } catch (error) {
        console.error('Error processing message:', error);
      }
    }
  });
}

// Handle TaskCreated event (for notifications)
async function handleTaskCreated(event) {
  try {
    // Validate event
    TaskCreatedEventSchema.parse(event);
    
    // Create notification record
    const notification = {
      id: `notif-${Date.now()}`,
      userId: event.userId,
      type: 'TASK_CREATED',
      title: 'New Task Created',
      message: `Task "${event.title}" has been created`,
      taskId: event.taskId,
      timestamp: new Date().toISOString(),
      read: false
    };
    
    notifications.push(notification);
    
    // Send notification via multiple channels (H3-REQ-004)
    await Promise.all([
      sendEmail(event.userId, 'New Task Created', `Task "${event.title}" has been created`),
      sendPushNotification(event.userId, 'New Task Created', `Task "${event.title}" has been created`)
    ]);
    
    console.log(`Handled TaskCreated event for task ${event.taskId}`);
  } catch (error) {
    console.error('Error handling TaskCreated event:', error);
  }
}

// Handle TaskAssigned event (H3-REQ-005)
async function handleTaskAssigned(event) {
  try {
    // Validate event
    TaskAssignedEventSchema.parse(event);
    
    // Create notification for the assignee
    const notification = {
      id: `notif-${Date.now()}`,
      userId: event.assigneeId, // Notification goes to the assignee
      type: 'TASK_ASSIGNED',
      title: 'Task Assigned to You',
      message: `You have been assigned to task "${event.taskTitle || 'Untitled Task'}"`,
      taskId: event.taskId,
      timestamp: new Date().toISOString(),
      read: false
    };
    
    notifications.push(notification);
    
    // Send notification to assignee
    await Promise.all([
      sendEmail(event.assigneeId, 'Task Assigned to You', `You have been assigned to task "${event.taskTitle || 'Untitled Task'}"`),
      sendPushNotification(event.assigneeId, 'Task Assigned', `You have been assigned to task "${event.taskTitle || 'Untitled Task'}"`),
      sendSMS(event.assigneePhone || '+1234567890', `You've been assigned to task: ${event.taskTitle || 'Untitled Task'}`)
    ]);
    
    console.log(`Handled TaskAssigned event for task ${event.taskId}, assignee: ${event.assigneeId}`);
  } catch (error) {
    console.error('Error handling TaskAssigned event:', error);
  }
}

// Handle DeadlineApproaching event (H3-REQ-004)
async function handleDeadlineApproaching(event) {
  try {
    // Validate event
    DeadlineApproachingEventSchema.parse(event);
    
    // Create notification record
    const notification = {
      id: `notif-${Date.now()}`,
      userId: event.userId,
      type: 'DEADLINE_APPROACHING',
      title: 'Task Deadline Approaching',
      message: `Deadline for "${event.taskTitle || 'Untitled Task'}" is approaching in ${event.timeUntilDeadline} minutes`,
      taskId: event.taskId,
      timestamp: new Date().toISOString(),
      read: false
    };
    
    notifications.push(notification);
    
    // Send notification via multiple channels (H3-REQ-004)
    await Promise.all([
      sendEmail(event.userId, 'Task Deadline Approaching', `Deadline for "${event.taskTitle || 'Untitled Task'}" is approaching in ${event.timeUntilDeadline} minutes`),
      sendPushNotification(event.userId, 'Deadline Approaching', `Deadline for "${event.taskTitle || 'Untitled Task'}" is approaching`),
      sendSMS(event.userPhone || '+1234567890', `Deadline for "${event.taskTitle || 'Untitled Task'}" is approaching in ${event.timeUntilDeadline} minutes`)
    ]);
    
    console.log(`Handled DeadlineApproaching event for task ${event.taskId}`);
  } catch (error) {
    console.error('Error handling DeadlineApproaching event:', error);
  }
}

// Initialize consumer connection
connectConsumer().catch(console.error);

// Routes

// GET /notifications - Retrieve all notifications for a user
app.get('/notifications', (req, res) => {
  const userId = req.query.userId;
  if (userId) {
    const userNotifications = notifications.filter(notif => notif.userId === userId);
    res.json(userNotifications);
  } else {
    res.json(notifications);
  }
});

// GET /notifications/:id - Retrieve a specific notification
app.get('/notifications/:id', (req, res) => {
  const notification = notifications.find(n => n.id === req.params.id);
  if (!notification) {
    return res.status(404).json({ error: 'Notification not found' });
  }
  res.json(notification);
});

// PUT /notifications/:id/read - Mark a notification as read
app.put('/notifications/:id/read', (req, res) => {
  const notification = notifications.find(n => n.id === req.params.id);
  if (!notification) {
    return res.status(404).json({ error: 'Notification not found' });
  }
  
  notification.read = true;
  notification.readAt = new Date().toISOString();
  res.json(notification);
});

// GET /health - Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Notification Service is running on port ${PORT}`);
});
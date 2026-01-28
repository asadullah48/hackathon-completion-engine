// services/task-service/src/app.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { producer } = require('../../shared/kafka-config/producer');
const { TaskCreatedEventSchema, TaskUpdatedEventSchema, TaskDeletedEventSchema } = require('../../shared/schemas/eventSchemas');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Connect to Kafka producer
async function connectProducer() {
  await producer.connect();
  console.log('Kafka producer connected');
}

// Initialize producer connection
connectProducer().catch(console.error);

// Mock database (in production, use PostgreSQL)
let tasks = [];
let taskIdCounter = 1;

// Helper function to validate and publish events
async function publishEvent(event) {
  try {
    await producer.send({
      topic: 'task-events',
      messages: [
        { value: JSON.stringify(event) }
      ]
    });
    console.log(`Event published: ${event.eventType} for task ${event.taskId}`);
  } catch (error) {
    console.error('Error publishing event:', error);
  }
}

// Routes

// GET /tasks - Retrieve all tasks
app.get('/tasks', (req, res) => {
  res.json(tasks);
});

// GET /tasks/:id - Retrieve a specific task
app.get('/tasks/:id', (req, res) => {
  const task = tasks.find(t => t.id === parseInt(req.params.id));
  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }
  res.json(task);
});

// POST /tasks - Create a new task (implements H3-REQ-001)
app.post('/tasks', async (req, res) => {
  const { title, description, priority, dueDate, assignedUsers = [], tags = [] } = req.body;
  
  if (!title) {
    return res.status(400).json({ error: 'Title is required' });
  }
  
  const newTask = {
    id: taskIdCounter++,
    title,
    description: description || '',
    priority: priority || 'medium',
    dueDate: dueDate || null,
    completed: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    assignedUsers,
    tags
  };
  
  tasks.push(newTask);
  
  // Publish TaskCreated event (H3-REQ-001)
  const event = {
    eventId: `evt-${Date.now()}`,
    eventType: 'TaskCreated',
    timestamp: new Date().toISOString(),
    taskId: newTask.id.toString(),
    userId: req.body.userId || 'anonymous',
    title: newTask.title,
    description: newTask.description,
    priority: newTask.priority,
    dueDate: newTask.dueDate,
    assignedUsers: newTask.assignedUsers,
    tags: newTask.tags
  };
  
  // Validate event before publishing
  try {
    TaskCreatedEventSchema.parse(event);
    await publishEvent(event);
  } catch (validationError) {
    console.error('Event validation error:', validationError);
    return res.status(400).json({ error: 'Invalid event data', details: validationError.errors });
  }
  
  res.status(201).json(newTask);
});

// PUT /tasks/:id - Update a task (implements H3-REQ-002)
app.put('/tasks/:id', async (req, res) => {
  const taskId = parseInt(req.params.id);
  const taskIndex = tasks.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  const { title, description, priority, dueDate, completed, assignedUsers, tags } = req.body;
  const oldTask = { ...tasks[taskIndex] };
  
  // Update task properties
  if (title !== undefined) tasks[taskIndex].title = title;
  if (description !== undefined) tasks[taskIndex].description = description;
  if (priority !== undefined) tasks[taskIndex].priority = priority;
  if (dueDate !== undefined) tasks[taskIndex].dueDate = dueDate;
  if (completed !== undefined) tasks[taskIndex].completed = completed;
  if (assignedUsers !== undefined) tasks[taskIndex].assignedUsers = assignedUsers;
  if (tags !== undefined) tasks[taskIndex].tags = tags;
  
  tasks[taskIndex].updatedAt = new Date().toISOString();
  
  const updatedTask = tasks[taskIndex];
  
  // Publish TaskUpdated event (H3-REQ-002)
  const updatedFields = {};
  if (title !== undefined) updatedFields.title = `${oldTask.title} -> ${title}`;
  if (description !== undefined) updatedFields.description = `${oldTask.description} -> ${description}`;
  if (priority !== undefined) updatedFields.priority = `${oldTask.priority} -> ${priority}`;
  if (dueDate !== undefined) updatedFields.dueDate = `${oldTask.dueDate} -> ${dueDate}`;
  if (completed !== undefined) updatedFields.completed = `${oldTask.completed} -> ${completed}`;
  if (assignedUsers !== undefined) updatedFields.assignedUsers = `${JSON.stringify(oldTask.assignedUsers)} -> ${JSON.stringify(assignedUsers)}`;
  if (tags !== undefined) updatedFields.tags = `${JSON.stringify(oldTask.tags)} -> ${JSON.stringify(tags)}`;
  
  const event = {
    eventId: `evt-${Date.now()}`,
    eventType: 'TaskUpdated',
    timestamp: new Date().toISOString(),
    taskId: updatedTask.id.toString(),
    userId: req.body.userId || 'anonymous',
    updatedFields,
    version: Date.now() // Simple versioning
  };
  
  // Validate event before publishing
  try {
    TaskUpdatedEventSchema.parse(event);
    await publishEvent(event);
  } catch (validationError) {
    console.error('Event validation error:', validationError);
    return res.status(400).json({ error: 'Invalid event data', details: validationError.errors });
  }
  
  res.json(updatedTask);
});

// DELETE /tasks/:id - Delete a task (implements H3-REQ-009)
app.delete('/tasks/:id', async (req, res) => {
  const taskId = parseInt(req.params.id);
  const taskIndex = tasks.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  const deletedTask = tasks.splice(taskIndex, 1)[0];
  
  // Publish TaskDeleted event (H3-REQ-009)
  const event = {
    eventId: `evt-${Date.now()}`,
    eventType: 'TaskDeleted',
    timestamp: new Date().toISOString(),
    taskId: deletedTask.id.toString(),
    userId: req.body.userId || 'anonymous'
  };
  
  // Validate event before publishing
  try {
    TaskDeletedEventSchema.parse(event);
    await publishEvent(event);
  } catch (validationError) {
    console.error('Event validation error:', validationError);
    return res.status(400).json({ error: 'Invalid event data', details: validationError.errors });
  }
  
  res.status(204).send();
});

// GET /health - Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Task Service is running on port ${PORT}`);
});
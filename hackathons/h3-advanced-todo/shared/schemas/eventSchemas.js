// shared/schemas/eventSchemas.js
const { z } = require('zod');

// Define event schemas using Zod for validation
const TaskCreatedEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.literal('TaskCreated'),
  timestamp: z.string().datetime(),
  taskId: z.string().uuid(),
  userId: z.string().uuid(),
  title: z.string(),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  dueDate: z.string().datetime().optional(),
  assignedUsers: z.array(z.string().uuid()).optional(),
  tags: z.array(z.string()).optional()
});

const TaskUpdatedEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.literal('TaskUpdated'),
  timestamp: z.string().datetime(),
  taskId: z.string().uuid(),
  userId: z.string().uuid(),
  updatedFields: z.record(z.any()),
  version: z.number()
});

const TaskDeletedEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.literal('TaskDeleted'),
  timestamp: z.string().datetime(),
  taskId: z.string().uuid(),
  userId: z.string().uuid()
});

const TaskAssignedEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.literal('TaskAssigned'),
  timestamp: z.string().datetime(),
  taskId: z.string().uuid(),
  assignerId: z.string().uuid(),
  assigneeId: z.string().uuid()
});

const DeadlineApproachingEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.literal('DeadlineApproaching'),
  timestamp: z.string().datetime(),
  taskId: z.string().uuid(),
  userId: z.string().uuid(),
  timeUntilDeadline: z.number()
});

module.exports = {
  TaskCreatedEventSchema,
  TaskUpdatedEventSchema,
  TaskDeletedEventSchema,
  TaskAssignedEventSchema,
  DeadlineApproachingEventSchema
};
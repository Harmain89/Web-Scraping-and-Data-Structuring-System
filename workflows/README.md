# Appointment Booking Follow-up System Workflows

This directory contains the production JSON definitions of the workflows created in the live n8n instance for the **Appointment Booking Follow-up System**.

## Workflows Included:
1. `appointment-booking-intake.json`: Webhook intake, data validation, Google Calendar availability query, double-booking prevention, booking record persistence, and multi-channel confirmations (WhatsApp + Gmail).
2. `appointment-booking-lifecycle.json`: Webhook lifecycle handler for appointment rescheduling and cancellations, slot conflict checks, and updated notifications.
3. `appointment-booking-reminders.json`: Scheduled cron reconciler for 24h & 1h reminders, post-appointment follow-up, and no-show recovery outreach.

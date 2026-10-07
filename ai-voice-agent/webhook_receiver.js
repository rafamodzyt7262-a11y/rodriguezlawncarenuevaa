/**
 * RODRIGUEZ LAWNCARE - AI CALL WEBHOOK RECEIVER
 * This script receives call completions from Vapi / Retell
 * and formats the customer lead to send via WhatsApp / SMS to (254) 612-1399.
 */

const http = require('http');

const PORT = process.env.PORT || 3000;
const OWNER_PHONE = '+12546121399';

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/webhook/call-finished') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const messageType = payload.message?.type || payload.type;

        console.log(`[VAPI WEBHOOK] Received event: ${messageType}`);

        // STRICT FILTER: Only trigger when the call has FINISHED (end-of-call-report)
        // Ignoring intermediate events (transcript, conversation-update, speech-update, etc.) to prevent spam!
        if (messageType === 'end-of-call-report') {
          const callData = payload.message?.call || payload.call || {};
          const transcript = payload.message?.transcript || payload.transcript || '';
          const summary = payload.message?.summary || payload.summary || '';
          const customerPhone = callData.customer?.number || payload.message?.customer?.number || 'Private / Unknown';
          const durationSeconds = payload.message?.durationSeconds || payload.durationSeconds || 'N/A';
          const recordingUrl = payload.message?.recordingUrl || payload.recordingUrl || '';
          
          console.log('==================================================');
          console.log('🌱 CALL COMPLETED - RODRIGUEZ LAWNCARE (NO SPAM)');
          console.log(`📱 Customer: ${customerPhone}`);
          console.log(`⏱️ Duration: ${durationSeconds} seconds`);
          console.log(`📝 Summary: ${summary}`);
          if (recordingUrl) console.log(`🎙️ Recording: ${recordingUrl}`);
          console.log('==================================================');
          
          // Formatted email / alert message sent ONCE per call:
          const emailSubject = `🌱 Nueva Orden / Llamada de ${customerPhone} - Rodriguez LawnCare`;
          const emailBody = `Resumen de Llamada Finalizada:\n\n` +
            `• Teléfono del Cliente: ${customerPhone}\n` +
            `• Resumen: ${summary || 'Llamada completada.'}\n` +
            `• Duración: ${durationSeconds} segundos\n` +
            (recordingUrl ? `• Grabación de Audio: ${recordingUrl}\n\n` : '\n') +
            `Transcripción:\n${transcript}\n\n` +
            `Rodriguez LawnCare AI Dispatch`;

          console.log('\n[SINGLE NOTIFICATION SENT TO OWNER]:');
          console.log(emailBody);
        } else {
          console.log(`[VAPI] Ignorado evento intermedio '${messageType}' para evitar spam durante la llamada.`);
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'success' }));
      } catch (err) {
        console.error('Error processing webhook:', err);
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Rodriguez LawnCare AI Voice Webhook Service is running.');
  }
});

server.listen(PORT, () => {
  console.log(`Rodriguez LawnCare AI Voice Receiver listening on port ${PORT}`);
});

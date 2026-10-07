# 🤖 Guía Paso a Paso: Activar el Bot de Llamadas de Rodriguez LawnCare

Con esta configuración, vas a tener un número de teléfono que contesta con Inteligencia Artificial las 24 horas del día en **inglés y español**, toma los datos del cliente (nombre, dirección, servicio y fecha) y te los envía a tu celular.

---

### Paso 1: Crea tu cuenta gratuita en Vapi.ai
1. Entra a **[vapi.ai](https://vapi.ai)** desde tu computadora o teléfono.
2. Dale clic a **Sign Up** (puedes registrarte con tu correo de Google en 1 segundo).
3. En cuanto entres a tu panel, verás que tienes **$10 dólares de saldo GRATIS** de regalo (suficiente para ~80 minutos de llamadas de prueba).

---

### Paso 2: Crear el Asistente de Voz (Cerebro)
1. En el menú de la izquierda, dale clic a **Assistants** -> **Create Assistant**.
2. Ponle de nombre: `Rodriguez LawnCare Receptionist`.
3. En la sección **First Message** (Primer mensaje que dice al contestar), pega esto:
   ```text
   Thank you for calling Rodriguez LawnCare! How can I help you with your yard today?
   ```
4. En la sección **System Prompt** (Instrucciones), abre el archivo `ai-voice-agent/system_prompt.txt` que te creé en tu proyecto y copia todo su texto. Pégalo en el cuadro de Vapi.
5. En la sección **Voice** (Voz), puedes elegir una voz bilingüe natural (por ejemplo la voz de Cartesia o ElevenLabs).
6. Dale clic en **Save** (Guardar).

---

### Paso 3: Probar el Bot GRATIS antes de comprar el número
En la esquina superior derecha de Vapi hay un botón verde que dice **"Talk to Assistant"** (Hablar con el Asistente):
* Púlsalo y habla por el micrófono de tu computadora o teléfono.
* Dile: *"Hola, necesito que me corten el pasto en Killeen"* o en inglés: *"Hey, I need my yard mowed and some trees trimmed"*.
* Verás cómo te responde en tiempo real con voz humana, te pregunta la dirección, la fecha y toma la orden.

---

### Paso 4: Comprar el número de teléfono ($1.15 / mes)
1. En el menú de Vapi, dale clic a **Phone Numbers**.
2. Dale clic a **Buy Number** (Comprar número).
3. En el código de área, pon: `254` (el área local de Killeen, Harker Heights, Copperas Cove y Belton).
4. Elige el número que más te guste. Cuesta solo **$1.15 al mes**.
5. Donde dice **Assistant**, selecciona: `Rodriguez LawnCare Receptionist`.
6. ¡Listo! A partir de ese segundo, cualquier persona que marque a ese número será atendida por tu bot de IA.

---

### Paso 5: Recibir las órdenes en tu correo sin SPAM (1 solo correo al terminar la llamada)
Para recibir las órdenes y resúmenes en tu correo (`arizmendir754@gmail.com`) o teléfono sin recibir spam mientras hablan:

#### ⚠️ IMPORTANTE: ¿Por qué te llegaba spam de correos durante la llamada?
Por defecto, Vapi envía notificaciones en tiempo real por **CADA PALABRA** que el cliente o el bot dicen (`transcript`, `conversation-update`, `speech-update`). Si tu automatización (Make.com, Zapier o Webhook) no tiene el filtro puesto, te envía un correo cada 5 segundos durante la llamada.

#### ✅ Solución en 2 pasos para que solo llegue 1 correo al colgar:

1. **En Vapi.ai (Configuración del Asistente):**
   * Ve a **Assistants** -> selecciona `Rodriguez LawnCare Receptionist`.
   * En la sección **Advanced** (o Server Messages):
   * **Desmarca** todas las casillas: quita `transcript`, `conversation-update`, `speech-update`, `status-update`, `tool-calls`.
   * **Deja marcada ÚNICAMENTE:** `end-of-call-report` (Reporte de Fin de Llamada).
   * Guarda los cambios (**Save**).

2. **En Make.com (si usas Make para enviar a Gmail):**
   * En tu escenario entre el **Webhook** y **Gmail**, haz clic en la línea que los conecta para agregar un **Filter (Filtro)**.
   * **Condición:** Pon `message.type` (o `type`).
   * **Operador:** `Equal to (Text operator)` (Igual a).
   * **Valor:** `end-of-call-report`
   * ¡Listo! Ahora Make.com ignorará cualquier mensaje intermedio y **únicamente enviará 1 correo final** cuando la llamada termine con el resumen completo, teléfono del cliente, fecha y dirección.

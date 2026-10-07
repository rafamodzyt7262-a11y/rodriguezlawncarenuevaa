# 🛑 Solución al Spam de Correos Durante la Llamada (Vapi.ai -> Gmail)

## 🔍 ¿Por qué pasaba esto?
Cuando alguien llama a tu número de Vapi, la IA procesa la voz en tiempo real. 
Por defecto, Vapi envía una notificación HTTP (Webhook) a tu servidor o a **Make.com / Zapier** cada vez que pasa un evento:
1. **`speech-update`**: Cada vez que el cliente o la IA empiezan a hablar.
2. **`transcript`**: Cada vez que el cliente o la IA dicen una sola frase.
3. **`conversation-update`**: Cada turno de la conversación.
4. **`status-update`**: Cuando la llamada conecta.
5. **`end-of-call-report`**: **Únicamente cuando cuelgan y la llamada termina**.

Si tu webhook o Make.com estaba recibiendo **todos** los eventos sin un filtro, cada palabra hablada disparaba una orden de *"Enviar correo"* a Gmail, inundando tu bandeja con 15 a 30 correos por llamada.

---

## 🛠️ Cómo arreglarlo en 2 minutos (Paso a Paso)

Tienes **dos filtros de seguridad**. Al activar ambos, garantizas al 100% que **solo llegue 1 solo correo al terminar la llamada** con el resumen completo.

---

### Paso 1: Configurar Vapi para que NO transmita eventos en vivo

1. Entra a tu cuenta en [vapi.ai](https://vapi.ai).
2. En el menú de la izquierda, entra a **Assistants** y haz clic en tu asistente (`Rodriguez LawnCare Receptionist`).
3. Ve a la pestaña **Advanced** (o busca la sección llamada **Server Messages** / **Webhooks**).
4. Verás una lista de casillas de verificación (checkboxes). 
   - ❌ **DESMARCA:** `transcript`
   - ❌ **DESMARCA:** `conversation-update`
   - ❌ **DESMARCA:** `speech-update`
   - ❌ **DESMARCA:** `status-update`
   - ❌ **DESMARCA:** `tool-calls` / `function-call`
   - ❌ **DESMARCA:** `model-output`
   - ✅ **DEJA MARCADA SOLAMENTE:** `end-of-call-report`
5. Haz clic en **Save** (Guardar) arriba a la derecha.

> 💡 **Resultado:** A partir de este momento, Vapi se queda en completo silencio durante la llamada y esperará a que el cliente cuelgue antes de enviar el paquete de información.

---

### Paso 2: Configurar el Filtro en Make.com (si usas Make para enviar a Gmail)

Si usas **Make.com** para recibir el webhook y enviar el correo a `arizmendir754@gmail.com`:

1. Abre tu escenario en Make.com.
2. Verás dos círculos:
   - Círculo 1: **Custom Webhook** (Vapi)
   - Círculo 2: **Gmail** (Send an email)
3. Haz clic en la **línea o la llave mecánica** que conecta el Webhook con Gmail (Set up a filter).
4. Configura el filtro exactamente así:
   - **Label (Etiqueta):** `Solo reporte final`
   - **Condition (Condición):** Haz clic y busca `message : type` (o `type`).
   - **Text operator (Operador):** Selecciona `Equal to` (Igual a).
   - **Value (Valor):** Escribe exactamente: `end-of-call-report`
5. Dale a **Save / OK**.
6. Guarda el escenario (**Save**) y asegúrate de que el switch esté en **ON**.

---

### Paso 3: Qué datos poner en el correo de Gmail (Plantilla Recomendada)

En el módulo de **Gmail -> Send an Email**, configúralo con estos datos para que te llegue super claro y ordenado:

* **To:** `arizmendir754@gmail.com`
* **Subject:** `🌱 Nueva Orden de Jardinería - {{message.customer.number}}`
* **Content:**
```text
¡Nueva llamada completada para Rodriguez LawnCare!

📱 Teléfono del Cliente: {{message.customer.number}}
⏱️ Duración: {{message.durationSeconds}} segundos

📝 RESUMEN DE LA ORDEN:
{{message.summary}}

🎙️ Grabación de la llamada:
{{message.recordingUrl}}

---
Rodriguez LawnCare AI Voice Dispatch
```

---

## 🧪 Cómo probar que quedó solucionado
1. Llama a tu número de Vapi desde tu celular.
2. Habla con el bot 30 segundos: *"Hola, quiero que me corten el pasto en Harker Heights el viernes, me llamo Carlos"*.
3. Espera mientras hablas: **revisa tu correo; verás que NO llega ningún mensaje mientras estás hablando**.
4. Cuelga la llamada.
5. A los 5-10 segundos de colgar, te llegará **un único correo** con el número de teléfono, el resumen del trabajo y la grabación.

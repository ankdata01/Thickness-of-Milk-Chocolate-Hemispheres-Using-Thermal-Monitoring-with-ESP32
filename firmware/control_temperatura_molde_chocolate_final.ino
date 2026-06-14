#include "max6675.h"
#include <math.h>

// ======================================================
// SISTEMA DE MONITOREO DE TEMPERATURA PARA MOLDE/CHOCOLATE
// ESP32 + MAX6675 + TERMOPAR TIPO K + RELEVADOR + LEDS
// ======================================================
// Modo recomendado para pruebas actuales: MONITOREO SEGURO
// No conectar 127 V ni calentador al relevador durante esta fase.
// ======================================================

// ------------------------------------------------------
// Pines del MAX6675
// ------------------------------------------------------
const int thermoSCK = 18;
const int thermoCS  = 5;
const int thermoSO  = 19;

// ------------------------------------------------------
// Pines de salida
// ------------------------------------------------------
const int RELAY_PIN = 26;
const int LED_RED   = 14;
const int LED_GREEN = 27;
const int LED_BLUE  = 25;

// ------------------------------------------------------
// Configuracion del relevador
// ------------------------------------------------------
// Tu modulo funciono como ACTIVE LOW:
// LOW  = relevador encendido
// HIGH = relevador apagado
const bool RELAY_ACTIVE_LOW = true;

// ------------------------------------------------------
// Modo de operacion
// ------------------------------------------------------
// 0 = Monitoreo seguro. El relevador siempre queda apagado.
// 1 = Control de calentamiento con histeresis.
// Para pruebas de molde frio, refrigerador, congelador y recipiente caliente,
// usar OPERATING_MODE = 0.
const int OPERATING_MODE = 0;

// ------------------------------------------------------
// Umbrales de clasificacion para MOLDE y CHOCOLATE
// ------------------------------------------------------
// Nota importante: el MAX6675 no es ideal para medir bajo 0 C.
// Si el molde viene del congelador, puede verse como 0-5 C o como
// una recuperacion rapida hacia temperatura ambiente.
const float VERY_COLD_MAX        = 5.0;   // Posible congelador / molde muy frio
const float REFRIGERATOR_MAX     = 10.0;  // Molde recien salido del refrigerador
const float COLD_MOLD_MAX        = 18.0;  // Molde frio
const float MOLD_RECOVERY_MAX    = 22.0;  // Molde en recuperacion termica
const float ROOM_TEMP_MAX        = 27.0;  // Molde a temperatura ambiente

const float CHOCOLATE_OK_LOW     = 29.0;  // Zona util aproximada para chocolate
const float CHOCOLATE_OK_HIGH    = 33.0;

const float HOT_CONTAINER_MIN    = 35.0;  // Recipiente caliente
const float WARNING_TEMP         = 45.0;  // Advertencia por temperatura alta
const float DANGER_TEMP          = 60.0;  // Peligro / sobretemperatura

// ------------------------------------------------------
// Histeresis para control de calentamiento
// Solo se usa si OPERATING_MODE = 1
// ------------------------------------------------------
const float CONTROL_ON_TEMP  = 30.0;  // Enciende si baja a este valor o menos
const float CONTROL_OFF_TEMP = 32.0;  // Apaga si sube a este valor o mas

// ------------------------------------------------------
// Objeto del sensor MAX6675
// ------------------------------------------------------
MAX6675 thermocouple(thermoSCK, thermoCS, thermoSO);

// ------------------------------------------------------
// Estado del sistema
// ------------------------------------------------------
bool relayState = false;

void setRelay(bool state) {
  relayState = state;

  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, state ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  }
}

void setLEDs(bool red, bool green, bool blue) {
  digitalWrite(LED_RED, red ? HIGH : LOW);
  digitalWrite(LED_GREEN, green ? HIGH : LOW);
  digitalWrite(LED_BLUE, blue ? HIGH : LOW);
}

void safeStop() {
  setRelay(false);
  setLEDs(true, false, false);  // Rojo = error / seguridad
}

String classifyTemperature(double tempC) {
  if (tempC <= VERY_COLD_MAX) {
    return "MOLDE MUY FRIO / POSIBLE CONGELADOR";
  }

  if (tempC <= REFRIGERATOR_MAX) {
    return "MOLDE RECIEN SACADO DEL REFRIGERADOR";
  }

  if (tempC <= COLD_MOLD_MAX) {
    return "MOLDE FRIO";
  }

  if (tempC <= MOLD_RECOVERY_MAX) {
    return "MOLDE EN RECUPERACION TERMICA";
  }

  if (tempC <= ROOM_TEMP_MAX) {
    return "MOLDE A TEMPERATURA AMBIENTE";
  }

  if (tempC < CHOCOLATE_OK_LOW) {
    return "CHOCOLATE FRIO / ZONA BAJA";
  }

  if (tempC >= CHOCOLATE_OK_LOW && tempC <= CHOCOLATE_OK_HIGH) {
    return "ZONA UTIL PARA CHOCOLATE";
  }

  if (tempC >= HOT_CONTAINER_MIN && tempC < WARNING_TEMP) {
    return "RECIPIENTE CALIENTE";
  }

  if (tempC >= WARNING_TEMP && tempC < DANGER_TEMP) {
    return "ADVERTENCIA: TEMPERATURA ALTA";
  }

  return "PELIGRO: SOBRETEMPERATURA";
}

void updateLEDs(double tempC) {
  if (tempC <= MOLD_RECOVERY_MAX) {
    setLEDs(false, false, true);     // Azul = molde frio / recuperacion termica
  }
  else if (tempC >= HOT_CONTAINER_MIN) {
    setLEDs(true, false, false);     // Rojo = recipiente caliente / advertencia
  }
  else {
    setLEDs(false, true, false);     // Verde = molde ambiente / zona segura
  }
}

void controlRelay(double tempC) {
  // Corte de seguridad por temperatura alta
  if (tempC >= WARNING_TEMP) {
    setRelay(false);
    return;
  }

  // Modo monitoreo seguro: relevador siempre apagado
  if (OPERATING_MODE == 0) {
    setRelay(false);
    return;
  }

  // Modo de control con histeresis
  if (OPERATING_MODE == 1) {
    if (tempC <= CONTROL_ON_TEMP) {
      setRelay(true);
    }

    if (tempC >= CONTROL_OFF_TEMP) {
      setRelay(false);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);

  // Estado seguro al iniciar
  setRelay(false);
  setLEDs(false, false, true);  // Azul = iniciando

  Serial.println();
  Serial.println("========================================");
  Serial.println(" SISTEMA DE TEMPERATURA MOLDE/CHOCOLATE");
  Serial.println(" ESP32 + MAX6675 + TERMOPAR + RELEVADOR");
  Serial.println("========================================");

  if (OPERATING_MODE == 0) {
    Serial.println("MODO: MONITOREO SEGURO");
    Serial.println("El relevador permanecera apagado.");
  } else {
    Serial.println("MODO: CONTROL DE CALENTAMIENTO");
    Serial.println("Usar solo con etapa de potencia segura.");
  }

  Serial.println("----------------------------------------");
  Serial.println("Pruebas posibles:");
  Serial.println("1. Molde a temperatura ambiente");
  Serial.println("2. Molde frio de refrigerador");
  Serial.println("3. Molde frio de congelador");
  Serial.println("4. Chocolate en recipiente caliente");
  Serial.println("5. Recipiente caliente");
  Serial.println("----------------------------------------");
  Serial.println("millis,tempC,estado,relevador");
  Serial.println("========================================");

  delay(1500);
}

void loop() {
  double tempC = thermocouple.readCelsius();

  if (isnan(tempC)) {
    safeStop();
    Serial.println("ERROR,NAN,Revisar termopar o conexiones,RELEVADOR OFF");
    delay(1000);
    return;
  }

  String estado = classifyTemperature(tempC);

  controlRelay(tempC);
  updateLEDs(tempC);

  Serial.print(millis());
  Serial.print(",");
  Serial.print(tempC);
  Serial.print(",");
  Serial.print(estado);
  Serial.print(",");

  if (relayState) {
    Serial.println("RELEVADOR ON");
  } else {
    Serial.println("RELEVADOR OFF");
  }

  delay(1000);
}

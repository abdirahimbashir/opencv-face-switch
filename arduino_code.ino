int ledPin = 7;   // D7
char command;
bool ledState = false;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);  // Initialize serial communication
  digitalWrite(ledPin, LOW);  // Start with LED off
  Serial.println("Arduino ready - waiting for commands...");
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.read();  // Read incoming command
    
    if (command == 'H') {  // Turn LED ON
      digitalWrite(ledPin, HIGH);
      ledState = true;
      Serial.println("LED ON");
    }
    else if (command == 'L') {  // Turn LED OFF
      digitalWrite(ledPin, LOW);
      ledState = false;
      Serial.println("LED OFF");
    }
  }
  
  // Optional: You can add a small delay
  delay(10);
}

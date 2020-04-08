char command;

void setup(){
  Serial.begin(115200);
  pinMode(2, OUTPUT);
}

void loop(){
  if(Serial.available()> 0){ 
    command = Serial.read();
    if(command == 'r')
      Serial.println(analogRead(A0));
    else if(command == '1')
      digitalWrite(2, HIGH);
    else if(command == '0')
      digitalWrite(2, LOW);
  }
}
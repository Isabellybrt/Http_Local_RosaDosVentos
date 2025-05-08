# Http_Local_RosaDosVentos
Leitura da posição do joystick da placa Bitdoglab usando servidor Flask

## 📦 Requisitos

- Python instalado
- Raspberry Pi Pico W configurada
- Código `picow_http_client.c` para a Pico W
- Flask (instalável com `pip install flask`)
- Flask-Cors ( `pip install flask-cors` )

## 🚀 Como rodar

1. No terminal, execute o servidor Flask:

   ```bash
   python server.py

2. O terminal exibirá o endereço IP do servidor, algo como:
   ```bash
    Running on http://10.0.0.5:5000

3. Copie esse IP e substitua no campo #define HOST no arquivo picow_http_client.c:
   ```bash
    #define HOST "10.0.0.5"

4. Compile e faça upload do código para a sua Pico W.

5. Execute o programa na placa. A comunicação entre a Pico W e o servidor Flask será iniciada automaticamente via Wi-Fi.

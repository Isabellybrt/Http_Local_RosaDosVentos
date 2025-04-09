import os
from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS  # Adicione esta linha

app = Flask(__name__)
CORS(app)  # Adicione esta linha para permitir requisições CORS

# Variável para armazenar a última direção detectada
last_direction = "Norte"
last_x = 2048
last_y = 2048

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rosa dos Ventos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: inline-block;
            max-width: 600px;
        }
        .compass {
            width: 300px;
            height: 300px;
            margin: 20px auto;
            position: relative;
            background-color: #f0f0f0;
            border-radius: 50%;
            border: 2px solid #333;
        }
        .direction {
            position: absolute;
            font-weight: bold;
            color: #333;
        }
        .north {
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
        }
        .south {
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
        }
        .east {
            top: 50%;
            right: 10px;
            transform: translateY(-50%);
        }
        .west {
            top: 50%;
            left: 10px;
            transform: translateY(-50%);
        }
        .northeast {
            top: 20%;
            right: 20%;
        }
        .northwest {
            top: 20%;
            left: 20%;
        }
        .southeast {
            bottom: 20%;
            right: 20%;
        }
        .southwest {
            bottom: 20%;
            left: 20%;
        }
        .center {
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            color: #e74c3c;
        }
        .arrow {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 30px;
            height: 120px;
            background-color: #e74c3c;
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            transform-origin: 50% 100%;
            transform: translate(-50%, -100%) rotate(0deg);
            transition: transform 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
            z-index: 10;
            border-radius: 2px;
        }
        /* Adicione ao seu CSS existente */
        .compass {
            position: relative;
            overflow: hidden; /* Evita que a seta vaze do container */
        }

        /* Círculo central para esconder a base da seta */
        .compass::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            background-color: #333;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            z-index: 15;
        }
                .current-direction {
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
            color: #2c3e50;
        }
        .coordinates {
            margin: 10px 0;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Rosa dos Ventos</h1>
        
        <div class="compass">
            <div class="direction north">N</div>
            <div class="direction northeast">NE</div>
            <div class="direction east">E</div>
            <div class="direction southeast">SE</div>
            <div class="direction south">S</div>
            <div class="direction southwest">SW</div>
            <div class="direction west">W</div>
            <div class="direction northwest">NW</div>
            <div class="direction center">•</div>
            <div class="arrow"></div>
        </div>
        
        <div class="current-direction">
            Direção atual: <span id="direction">Norte</span>
        </div>
        
        <div class="coordinates" id="coordinates">
            X: 2048, Y: 2048
        </div>
    </div>

    <script>
        // Função para atualizar a direção
        async function updateDirection() {
            try {
                const response = await fetch('/data');
                if (!response.ok) {
                    throw new Error('Erro na requisição');
                }
                const data = await response.json();
                
                console.log('Dados recebidos:', data); // Log para depuração
                
                document.getElementById('direction').textContent = data.direction;
                document.getElementById('coordinates').textContent = `X: ${data.x}, Y: ${data.y}`;
                
                // Dentro da função updateDirection()
                const arrow = document.querySelector('.arrow');
                const directions = {
                    'Norte': 0,
                    'Nordeste': 45,
                    'Leste': 90,
                    'Sudeste': 135,
                    'Sul': 180,
                    'Sudoeste': 225,
                    'Oeste': 270,
                    'Noroeste': 315,
                    'Centro': 0
                };

                // Suaviza a transição entre ângulos (evita giros desnecessários)
                let currentAngle = directions[data.direction] || 0;
                let targetAngle = directions[data.direction] || 0;

                // Calcula o caminho mais curto para a rotação
                let diff = (targetAngle - currentAngle + 360) % 360;
                if (diff > 180) diff -= 360;

                // Aplica a rotação suavemente
                arrow.style.transform = `translate(-50%, -100%) rotate(${currentAngle + diff}deg)`;
            } catch (error) {
                console.error('Erro ao atualizar direção:', error);
            }
        }

        // Atualizar a cada 500ms e quando a página carrega
        updateDirection(); // Chamada inicial
        setInterval(updateDirection, 500); // Atualização periódica

        // Log para verificar se o script está carregando
        console.log('Script carregado com sucesso');
    </script>
</body>
</html>
"""

@app.route("/data", methods=["GET"])
def get_direction():
    global last_direction, last_x, last_y
    
    # Se receber parâmetros, atualiza os valores
    if 'x' in request.args and 'y' in request.args:
        last_x = request.args.get("x", type=int, default=2048)
        last_y = request.args.get("y", type=int, default=2048)
    
    # Lógica para determinar a direção
    ADC_MAX = 4095  # 12-bit ADC
    
    if last_y < ADC_MAX / 4 and last_x < ADC_MAX / 4:
        direction = "Sudoeste"
    elif last_y < ADC_MAX / 4 and last_x > 3 * ADC_MAX / 4:
        direction = "Sudeste"
    elif last_y > 3 * ADC_MAX / 4 and last_x < ADC_MAX / 4:
        direction = "Noroeste"
    elif last_y > 3 * ADC_MAX / 4 and last_x > 3 * ADC_MAX / 4:
        direction = "Nordeste"
    elif last_y < ADC_MAX / 3:
        direction = "Sul"
    elif last_y > 2 * ADC_MAX / 3:
        direction = "Norte"
    elif last_x < ADC_MAX / 3:
        direction = "Oeste"
    elif last_x > 2 * ADC_MAX / 3:
        direction = "Leste"
    else:
        direction = "Centro"
    
    last_direction = direction
    
    # Debug no console do servidor
    print(f"Retornando dados - X: {last_x}, Y: {last_y}, Direção: {direction}")
    
    response = jsonify({
        "direction": direction,
        "x": last_x,
        "y": last_y
    })
    
    # Configura headers para evitar cache
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@app.route("/", methods=["GET"])
def pagina_inicial():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
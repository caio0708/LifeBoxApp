# LifeBoxApp
Este repositório contém o código-fonte do "LifeBox", um aplicativo desenvolvido em Kivy, projetado para gerenciar informações de caixas com temperatura controlada. O LifeBox oferece uma solução completa para monitorar as temperaturas das caixas e executar ações específicas com base nesses dados. O aplicativo é destinado tanto a operadores quanto a médicos, fornecendo funcionalidades abrangentes para controle e supervisão.

# Funcionalidades do Aplicativo
# Tela de Login
Faça login com um nome de usuário e senha.
O aplicativo diferencia entre operadores e médicos, garantindo permissões adequadas.

# Cadastro de Usuários
Cadastre novos operadores e médicos por meio da tela de registro.
Para o cadastro, insira as seguintes informações:
Nome de Usuário: Escolha um nome de usuário único, com um limite máximo de 10 caracteres.
Senha: Defina uma senha de autenticação com exatamente 4 dígitos numéricos.
Tipo de Usuário: Escolha entre "Operador" ou "Médico" para configurar o nível de acesso.
Senha de Autorização (Médicos): Médicos devem fornecer uma senha de autorização (medico123) para registro.

# Tela de Operador
Os operadores têm acesso a funcionalidades essenciais, incluindo:
Monitoramento da temperatura da caixa.
Controle do estado dos LEDs.
Visualização do status do potenciômetro.

# Tela de Médico
Médicos podem realizar as seguintes ações:
Visualizar dados armazenados relacionados às caixas com temperatura controlada.
Editar informações sobre caixas específicas, incluindo objeto e temperatura segura.
O "LifeBox" oferece uma solução flexível e completa para o gerenciamento de caixas com temperatura controlada, permitindo que operadores monitorem e controlem os aspectos essenciais, enquanto médicos têm acesso a informações detalhadas para tomada de decisões informadas.

# Como Usar
Clone este repositório para o seu ambiente local.
Certifique-se de ter o Python e o Kivy instalados.
Execute o aplicativo com o comando python main.py a partir do diretório do projeto.

# Contribuição
Se você deseja contribuir para o projeto "LifeBoxApp", sinta-se à vontade para criar pull requests ou relatar problemas na seção de problemas deste repositório.

# Licença
Este projeto é licenciado sob a Licença MIT. Consulte o arquivo LICENSE para obter detalhes.

Agradecemos por usar o "LifeBoxApp". Esperamos que este aplicativo seja útil para monitorar e gerenciar caixas com temperatura controlada de forma eficaz e conveniente.

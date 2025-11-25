Heroes RPG - GUI Edition
Um jogo de RPG baseado em turnos com interface gráfica desenvolvido em Python usando Tkinter.

🎮 Sobre o Jogo
Heroes RPG é um jogo de RPG tático onde você controla um grupo de heróis através de 10 andares de uma masmorra, enfrentando monstros cada vez mais poderosos. Cada herói pertence a uma classe única com habilidades especiais e pode equipar itens para melhorar seus atributos.

✨ Funcionalidades
🎯 Sistema de Combate
Sistema de turnos baseado em velocidade

Três classes de heróis: Guerreiro, Mago e Arqueiro

Habilidades únicas por classe

Sistema de crítico e rolagens de dados

Efeitos de status: Queimação, buffs de ataque/defesa, etc.

🛡️ Sistema de Progressão
Sistema de níveis (até nível 20)

Distribuição automática de pontos de atributo

Ganho de experiência por derrotar monstros

Escalonamento de monstros por andar

🎒 Sistema de Itens
Equipamentos aleatórios com bônus variados

Poções de cura para uso em batalha

Inventário gerenciável para cada herói

Equipamento automático de itens melhores

👥 Classes Disponíveis
🗡️ Guerreiro
Habilidade de Classe: Chamado do Líder - Buffa aliados com ATK e DEF

Habilidade de Arma: Coronhada - Ataque extra com dano adicional

🔮 Mago
Habilidade de Classe: Bola de Fogo - Dano mágico que ignora DEF

Habilidade de Arma: Ignis - Imbui armas aliadas com elemento fogo

🏹 Arqueiro
Habilidade de Classe: Olho de Águia - Garante 100% de crítico

Passiva: Chance de ataque duplo

🚀 Como Executar
Pré-requisitos
Python 3.7 ou superior

Tkinter (geralmente incluído na instalação padrão do Python)

Instalação e Execução
bash
# Clone o repositório

git clone https://github.com/BigchakaDeV/heroes

# Entre no diretório
cd heroes-rpg

# Execute o jogo
python heroeis.py
🎮 Como Jogar
Criação de Personagem
Escolha um nome para seu herói principal

Selecione uma classe entre Guerreiro, Mago ou Arqueiro

Role os status ou use os gerados automaticamente

Comece a aventura com dois aliados das outras classes

Durante a Batalha
Atacar: Causa dano básico ao inimigo selecionado

Habilidade de Classe: Usa habilidade especial da classe

Habilidade de Arma: Usa habilidade especial da arma

Curar: Usa poção de cura (quantidade limitada)

Passar: Passa o turno sem ação

Gerenciamento
Inventário: Acessível clicando em "Abrir Inventário" no painel do herói

Equipamento automático: Itens melhores são equipados automaticamente

Distribuição de XP: Automática ao subir de nível

🏗️ Estrutura do Projeto
text
heroeis.py
├── Classes Base
│   ├── Personagem (ABC)
│   ├── Guerreiro, Mago, Arqueiro
│   └── Monstro, Orc, Ogro, Bruxa
├── Sistema de Itens
│   ├── Equipamento, Arma, Armadura
│   ├── Botas, Luvas
│   └── Poção de Cura
├── Sistema de Batalha
│   ├── Batalha (gerenciador de turnos)
│   ├── Cálculo de dano
│   └── Efeitos de status
└── Interface
    └── GameGUI (Tkinter)

🎯 Objetivo
Derrote todos os 10 andares de monstros para vencer o jogo! Monstros ficam mais fortes a cada andar, então equipe seus heróis com os melhores itens e use estratégias inteligentes para sobreviver.

🔧 Possíveis Melhorias Futuras
Sistema de salvamento

Mais classes e habilidades

Chefes únicos por andar

Sistema de crafting

Modo multiplayer

Sons e música

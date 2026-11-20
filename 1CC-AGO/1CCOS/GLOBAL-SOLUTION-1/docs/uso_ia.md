# Uso de Inteligência Artificial

Este documento registra como a IA apoiou o desenvolvimento do Neighborhood Action Dashboard e como os resultados foram verificados, conforme a orientação da Global Solution.

## Ferramenta utilizada

- **Claude** (Anthropic), usado em conversa por uma integrante da equipe.

## Como a IA apoiou

| Etapa | O que a IA fez | O que a equipe decidiu |
|---|---|---|
| Leitura do enunciado | resumiu os requisitos e montou um checklist | prioridades e prazo |
| Dados fictícios | gerou as 12 ocorrências da Comunidade Vale Verde, os 10 eventos do histórico e os 2 registros inconsistentes | o grupo revisou e manteve a Comunidade Vale Verde, as quatro categorias e os cenários gerados |
| Código | escreveu uma primeira versão de `src/sistema.py` (estruturas, validações, menu e indicadores) | o grupo leu o código, testou as opções do menu e manteve a versão sem alterações |
| Documentação | redigiu o README, este arquivo e o roteiro do vídeo | revisão do texto e das justificativas |

## Como os resultados foram verificados

### Verificações feitas durante o desenvolvimento

Os cenários abaixo foram executados no terminal, e a saída foi conferida com os valores esperados:

- [x] Carregamento: 12 ocorrências válidas, 10 eventos e 2 registros inconsistentes separados (`013` sem categoria; `014` com situação `RESOLVIDO`).
- [x] Fluxo do enunciado: cadastrar uma demanda de iluminação na Praça Central, filtrar as abertas de iluminação, mudar a situação para "em análise" e ver os indicadores atualizados.
- [x] Indicadores conferidos à mão: 4/3/3/2 por categoria; 5/4/3 por situação; tempo médio de conclusão = (7 + 8 + 5) ÷ 3 = 6,7 dias; espera média das pendentes = 156 ÷ 9 = 17,3 dias.
- [x] Erros tratados: código inexistente, situação não permitida, ocorrência concluída, cadastro sem categoria e descrição com telefone ou e-mail.
- [x] Fila: a triagem examina primeiro a ocorrência registrada há mais tempo.
- [x] Pilha: as últimas atualizações aparecem da mais recente para a mais antiga.

### Verificações feitas pela equipe

A equipe deve marcar cada item depois de fazer a verificação de verdade:

- [X] Rodamos `python src/sistema.py` no nosso computador, sem erros.
- [X] Testamos todas as opções do menu.
- [X] Conferimos os indicadores com uma calculadora.
- [X] Lemos o código e conseguimos explicar cada estrutura de dados e a expressão booleana do filtro.
- [X] Revisamos o README e ajustamos o que não representava as decisões do grupo.

## Responsabilidade

A IA foi usada como ferramenta de apoio. A equipe é responsável por entender, testar e justificar o código, os dados e as análises apresentados, e conseguir explicá-los no vídeo.

# Roteiro do vídeo — Neighborhood Action Dashboard

O roteiro tem cerca de 5 minutos. Basta uma pessoa apresentar, com a tela compartilhada e o terminal aberto na pasta `GLOBAL-SOLUTION-1`.

**Antes de gravar**
- Rode `python src/sistema.py` uma vez para conferir que funciona.
- Aumente a fonte do terminal (Ctrl + `+`) para ficar legível no vídeo.
- Deixe o README aberto numa aba do navegador.
- Publique no YouTube como **Não listado** e cole o link no README e no .TXT de entrega.

---

## 1. Abertura (0:00 a 0:30)

**Mostrar:** o README no GitHub.

> "Olá, somos o Grupo 38 de Ciência da Computação da FIAP. Este é o Neighborhood Action Dashboard, um painel para registrar e acompanhar demandas de melhoria na Comunidade Vale Verde, um bairro fictício. O problema é que hoje os relatos de postes apagados, calçadas sem rampa ou lixo acumulado ficam espalhados, e ninguém sabe o que já foi visto ou resolvido."

## 2. Dados e estruturas (0:30 a 1:30)

**Mostrar:** `data/ocorrencias.csv` e depois a tabela de estruturas no README.

> "As ocorrências ficam num arquivo CSV com código, categoria, descrição, bairro, local genérico, dia de abertura e situação. São 12 registros válidos e 2 com problema de propósito, para testar a validação."

> "No código, usamos uma **lista** para guardar todas as ocorrências e percorrê-las; um **dicionário** para buscar direto pelo código; uma **fila** para a triagem, em que quem foi registrado primeiro é examinado primeiro; uma **pilha** para as últimas atualizações, com a mais recente no topo; uma **hierarquia** bairro, categoria, ocorrências; e uma **matriz** que cruza categoria com situação."

## 3. Demonstração (1:30 a 3:45)

**Mostrar:** o terminal.

1. **Iniciar:** `python src/sistema.py`
   > "Ao abrir, o sistema já avisa que carregou 12 ocorrências e separou 2 inconsistentes."
2. **Opção 10, registros inconsistentes:**
   > "O 013 está sem categoria, e o 014 tem a situação 'RESOLVIDO', que não existe no padrão. Eles ficam fora das contagens."
3. **Opção 4, cadastrar:** categoria 1 (Iluminação), descrição "Poste apagado em frente ao banco da praça", bairro "Jardim das Acácias", local "Praça Central".
   > "O código 015 é gerado automaticamente, e toda demanda nova entra como Aberta e vai para o fim da fila."
4. **Opção 4 de novo, com dado pessoal:** descrição "Ligar para 11987654321".
   > "Aqui a regra de privacidade recusa o cadastro: o painel não guarda telefones nem e-mails."
5. **Opção 3, filtrar:** categoria 1, situação 1.
   > "Esse filtro usa a expressão booleana: categoria vazia OU igual, E situação vazia OU igual."
6. **Opção 6, atualizar:** código 015, Em análise, observação "equipe acionada".
   > "A mudança só acontece se for permitida. Uma ocorrência concluída, por exemplo, não muda mais."
7. **Opção 7, últimas atualizações:**
   > "Essa é a pilha: a mudança que acabamos de fazer aparece no topo."
8. **Opção 8, hierarquia:**
   > "Aqui vemos onde os problemas se concentram em cada bairro."
9. **Opção 9, indicadores:** mostre a matriz e a interpretação.

## 4. Indicadores e interpretação (3:45 a 4:20)

> "As proporções são quantidade dividida pelo total vezes 100. O tempo médio até a conclusão é a soma dos dias entre abertura e conclusão dividida pelo número de concluídas: 6,7 dias. Já as pendentes esperam em média mais de 15 dias, ou seja, a fila está acumulando. Iluminação e acessibilidade são as prioridades, e acessibilidade ainda não teve nenhuma demanda concluída."

## 5. Acessibilidade, privacidade e conclusão (4:20 a 5:00)

**Mostrar:** a seção de acessibilidade do README.

> "As mensagens começam com OK, ERRO ou AVISO, em texto e sem depender de cor, e as opções aceitam número ou nome, com ou sem acento. O sistema não guarda quem relatou, usa locais genéricos e recusa dados pessoais. Como limitações: os dados são fictícios, as mudanças não ficam salvas no arquivo e não há integração com a prefeitura. Obrigado!"

**Opção 0, sair.**

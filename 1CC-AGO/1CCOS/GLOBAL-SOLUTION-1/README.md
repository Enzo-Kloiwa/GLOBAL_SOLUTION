# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="../../../assets/logo-fiap.png"
       alt="FIAP - Faculdade de Informática e Administração Paulista"
       width="40%">
</a>
</p>

<br>

# Neighborhood Action Dashboard — Comunidade Vale Verde

Global Solution 2026.2 · Desafio CitizenTech

## Grupo 34

## 👨‍🎓 Integrantes:
- Enzo Yugi Kloiwa — RM 574398
- Luke Malaquias Lage — RM 574356
- Rafaela Aparecida dos Santos Atanásio — RM 574868
- Yasmin Sampaio Barbieri — RM 576282

## 👩‍🏫 Professores:

### Tutor(a)
- André Tritiack

### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

---

## 📜 Descrição

### A comunidade simulada

A **Comunidade Vale Verde** é um bairro fictício formado por três áreas: **Vale Verde Centro**, **Jardim das Acácias** e **Vila Nova Esperança**. Ali, moradores relatam problemas do dia a dia nos espaços coletivos: postes apagados, calçadas sem rampa, lixo acumulado e equipamentos públicos quebrados.

### O problema

Hoje esses relatos ficam espalhados: um morador avisa no grupo do bairro, outro comenta na associação, e ninguém sabe o que já foi visto, o que está parado e o que foi resolvido. Sem organização, as prioridades não ficam claras e quem relatou não consegue acompanhar.

### A solução

O **Neighborhood Action Dashboard** é um painel comunitário em Python, que roda no terminal. Ele:

- carrega as ocorrências de um arquivo e **valida** cada registro;
- permite **cadastrar**, **buscar por código** e **filtrar** por categoria e situação;
- organiza uma **fila de triagem** das demandas ainda não examinadas;
- **atualiza a situação** de cada demanda e guarda o **histórico** das mudanças;
- mostra **indicadores** (totais, proporções, pendências e tempos médios) com uma interpretação dos números.

### Público beneficiado

Moradores, que acompanham o andamento do que relataram; associações de bairro, que organizam e priorizam as demandas; e voluntários ou equipes de manutenção, que veem o que está pendente há mais tempo.

> O sistema é um protótipo acadêmico. Os dados são **fictícios**, não há integração com prefeitura ou órgãos públicos e o painel não promete atendimento das demandas.

---

## 📁 Estrutura de pastas

```
GLOBAL-SOLUTION-1/
├── README.md                  ← este arquivo
├── src/
│   └── sistema.py             ← programa principal (python src/sistema.py)
├── data/
│   ├── ocorrencias.csv        ← 14 registros (12 válidos + 2 inconsistentes)
│   └── historico.csv          ← 10 eventos de mudança de situação
└── docs/
    ├── uso_ia.md              ← como a IA apoiou o desenvolvimento
    ├── roteiro_video.md       ← roteiro da apresentação em vídeo
    └── exemplo_execucao.txt   ← execução completa de exemplo
```

---

## 🗃️ Dados e formato

O sistema lê dois arquivos **CSV separados por ponto e vírgula** (`;`), porque as descrições podem conter vírgulas.

### `data/ocorrencias.csv`

| Campo | Obrigatório | Exemplo | Regra |
|---|---|---|---|
| `codigo` | sim | `005` | único, três dígitos |
| `categoria` | sim | `ILUMINACAO` | uma das 4 categorias padronizadas |
| `descricao` | sim | `Luminária piscando no ponto de ônibus` | sem dados pessoais |
| `bairro` | sim | `Vila Nova Esperança` | área da comunidade |
| `local` | sim | `Ponto de ônibus da avenida principal` | local genérico, sem endereço exato |
| `dia_abertura` | sim | `7` | número entre 1 e o dia atual da simulação |
| `status` | sim | `ABERTA` | uma das 3 situações padronizadas |

### `data/historico.csv`

`codigo;dia;status_anterior;status_novo;observacao`, com um evento por linha.

### Valores padronizados

| Categoria (código) | Exibição |
|---|---|
| `ILUMINACAO` | Iluminação |
| `ACESSIBILIDADE` | Acessibilidade |
| `LIMPEZA` | Limpeza |
| `CONSERVACAO` | Conservação (de espaços coletivos) |

| Situação (código) | Significado | Pode mudar para |
|---|---|---|
| `ABERTA` | registrada e ainda não examinada pela equipe | Em análise |
| `EM_ANALISE` | examinada, com atendimento em avaliação ou andamento | Concluída ou de volta para Aberta |
| `CONCLUIDA` | problema resolvido e demanda encerrada | nenhuma (situação final) |

### Dados simulados

- **12 ocorrências válidas** distribuídas entre iluminação (4), acessibilidade (3), limpeza (3) e conservação (2).
- **3 situações**: 5 abertas, 4 em análise e 3 concluídas.
- **10 eventos** no histórico.
- **2 registros inconsistentes** de propósito: o `013` está sem categoria, e o `014` tem a situação desconhecida `RESOLVIDO`. A validação identifica os dois e os separa das contagens (opção 10 do menu).

---

## 🧱 Estruturas de dados e justificativa

| Estrutura | Onde no código | Para que serve | Por que essa estrutura |
|---|---|---|---|
| **Lista** | `painel["ocorrencias"]` | todas as ocorrências válidas | percorrer o conjunto inteiro na listagem, nos filtros e nos indicadores |
| **Dicionário** | `painel["indice"]` | código → ocorrência | busca direta por código, sem percorrer a lista |
| **Fila (FIFO)** | `painel["fila_triagem"]` | demandas abertas ainda não examinadas | quem foi registrado primeiro é examinado primeiro: justo com quem relatou antes |
| **Pilha (LIFO)** | `painel["pilha_eventos"]` | últimas atualizações | o evento mais recente fica no topo e é o primeiro a ser consultado |
| **Hierarquia** (dicionário de dicionários) | `montar_hierarquia()` | bairro → categoria → códigos | mostra onde os problemas se concentram em cada área da comunidade |
| **Matriz** (lista de listas) | `montar_matriz()` | quantidade por categoria × situação | resume o cruzamento das duas classificações numa tabela só |
| **Tuplas** | `STATUS`, `TRANSICOES`, `CAMPOS_OBRIGATORIOS` | informações fixas | valores que não devem mudar durante a execução |

A fila e a pilha foram feitas com listas do Python: a fila usa `append` para entrar no fim e lê o primeiro elemento (`fila[0]`); a pilha usa `append` para empilhar e lê a partir do último elemento.

---

## 🧠 Regras lógicas

### Cadastro e validação

Toda ocorrência passa pela função `validar_ocorrencia`, tanto as que vêm do arquivo quanto as cadastradas no menu. Ela devolve a lista de problemas encontrados; se a lista estiver vazia, o registro é aceito.

| Condição verificada | Mensagem | Por quê |
|---|---|---|
| campo obrigatório vazio | `campo obrigatório 'categoria' ausente` | sem esse campo a ocorrência não pode ser classificada nem acompanhada |
| categoria fora da lista | `categoria desconhecida` | os indicadores só funcionam com valores padronizados |
| situação fora da lista | `situação desconhecida 'RESOLVIDO'` | impede situações que o sistema não sabe tratar |
| dia que não é número ou está fora de 1 até o dia atual | `dia de abertura inválido` | uma demanda não pode ter sido aberta no futuro |
| código repetido | `código já existe` | o código precisa identificar uma única ocorrência |
| e-mail ou 8+ dígitos seguidos na descrição ou no local | `parece conter dado pessoal` | regra de privacidade: o painel não guarda contatos |

Toda ocorrência nova entra como **Aberta**, com o dia atual da simulação e um código gerado automaticamente (maior código já usado + 1).

### Expressões booleanas

O sistema usa `and`, `or` e `not` em várias condições. Três delas:

**1. Filtro por categoria e situação** (função `filtrar`), a expressão documentada:

```python
(categoria is None or oc["categoria"] == categoria) and (status is None or oc["status"] == status)
```

Cada parênteses diz "este filtro está vazio **ou** a ocorrência bate com ele". O `and` exige que os dois lados sejam verdadeiros. Assim, um único código atende quatro consultas: só categoria, só situação, as duas ou nenhuma (lista tudo).

**2. Dia de abertura válido** (função `validar_ocorrencia`):

```python
dia_valido = dia.isdigit() and 1 <= int(dia) <= painel["dia_atual"]
if dia and not dia_valido: ...
```

**3. Privacidade** (função `contem_dado_pessoal`):

```python
return "@" in texto or maior_sequencia >= 8
```

Basta uma das condições para o texto ser recusado.

Também há `or` no cálculo de pendências (`status == "ABERTA" or status == "EM_ANALISE"`) e `and` na leitura do histórico (o evento só entra se o código existir **e** as duas situações forem conhecidas).

### Consulta

- **Busca por código:** acesso direto pelo dicionário. O código pode ser digitado como `5`, `05` ou `005`. Se não existir, o sistema avisa `Ocorrência '999' não encontrada.`
- **Filtro:** categoria e situação escolhidas por número ou por nome, com ou sem acento. Enter significa "todas".

### Atualização de situação

A função `atualizar_status` usa `if / elif / else` para decidir:

```
if   situação desconhecida          -> recusa
elif situação igual à atual          -> recusa ("já está como...")
elif mudança fora de TRANSICOES      -> recusa ("mudança não permitida")
else                                 -> muda, registra no histórico e na pilha
```

Quando uma demanda sai de **Aberta**, ela deixa a fila de triagem. Se voltar para **Aberta**, entra de novo no fim da fila. Uma demanda **Concluída** não pode mais mudar.

---

## 📊 Indicadores

| Indicador | Fórmula | Resultado inicial (dia 30) |
|---|---|---|
| Total por categoria | contagem com laço `for` | Iluminação 4 · Acessibilidade 3 · Limpeza 3 · Conservação 2 |
| Proporção por categoria | quantidade ÷ total × 100 | 33,3% · 25,0% · 25,0% · 16,7% |
| Total e proporção por situação | quantidade ÷ total × 100 | Abertas 5 (41,7%) · Em análise 4 (33,3%) · Concluídas 3 (25,0%) |
| Pendências | abertas + em análise | 9 |
| Tempo médio até a conclusão | Σ (dia de conclusão − dia de abertura) ÷ nº de concluídas | (7 + 8 + 5) ÷ 3 = **6,7 dias** |
| Espera média das pendentes | Σ (dia atual − dia de abertura) ÷ nº de pendentes | 156 ÷ 9 = **17,3 dias** |

O dia de conclusão vem do histórico: é o dia do evento que levou a ocorrência para **Concluída**.

**Matriz categoria × situação** (dia 30):

| Categoria | Aberta | Em análise | Concluída | Total |
|---|---|---|---|---|
| Iluminação | 2 | 1 | 1 | 4 |
| Acessibilidade | 2 | 1 | 0 | 3 |
| Limpeza | 0 | 1 | 2 | 3 |
| Conservação | 1 | 1 | 0 | 2 |

### Interpretação

- **Iluminação** é a categoria mais relatada (4 de 12) e, junto com **Acessibilidade**, a que mais acumula pendências (3 cada).
- **Acessibilidade** ainda não teve nenhuma demanda concluída. Isso merece atenção, porque afeta diretamente pessoas com deficiência ou mobilidade reduzida.
- Só **25%** das demandas foram concluídas.
- As pendentes já esperam, em média, **17,3 dias**, bem mais que os **6,7 dias** que as concluídas levaram. É sinal de que a fila está acumulando mais rápido do que é atendida.

---

## 🔧 Como executar o código

**Pré-requisito:** Python 3.8 ou mais recente. Não é preciso instalar nenhum pacote.

```bash
git clone https://github.com/Enzo-Kloiwa/GLOBAL_SOLUTION.git
cd GLOBAL_SOLUTION/1CC-AGO/1CCOS/GLOBAL-SOLUTION-1
python src/sistema.py
```

No Windows, se `python` não funcionar, use `py src/sistema.py`.

### Menu

```
  1) Listar todas as ocorrências
  2) Buscar ocorrência por código
  3) Filtrar por categoria e/ou situação
  4) Cadastrar nova ocorrência
  5) Triagem: examinar a próxima da fila
  6) Atualizar a situação de uma ocorrência
  7) Ver últimas atualizações
  8) Ver hierarquia bairro -> categoria
  9) Painel de indicadores
 10) Ver registros inconsistentes
 11) Avançar o dia da simulação
 12) Ajuda: situações e regras
  0) Sair
```

---

## 💻 Exemplo de execução

O exemplo segue o fluxo sugerido no enunciado. A execução completa está em [`docs/exemplo_execucao.txt`](docs/exemplo_execucao.txt).

**Cadastro (opção 4)**

```
Categoria:
  1) Iluminação
  ...
Escolha: 1
Descrição breve: Poste apagado em frente ao banco da praça
Bairro: Jardim das Acácias
Local genérico (ex.: Praça Central): Praça Central
[OK] Ocorrência 015 cadastrada como 'Aberta' no dia 30 e colocada na fila de triagem.
```

**Consulta: iluminação aberta (opção 3)**

```
Filtro: categoria = Iluminação | situação = Aberta
Cód.  Categoria       Bairro               Local                        Situação
005   Iluminação      Vila Nova Esperança  Ponto de ônibus da avenida … Aberta
012   Iluminação      Vila Nova Esperança  Quadra poliesportiva         Aberta
015   Iluminação      Jardim das Acácias   Praça Central                Aberta
Total: 3 ocorrência(s).
```

**Alteração de situação (opção 6)**

```
Código da ocorrência: 015
Situação atual: Aberta
Mudar para:
  1) Em análise
Escolha: 1
Observação (opcional): equipe de iluminação acionada
[OK] Ocorrência 015: 'Aberta' -> 'Em análise' (dia 30).
```

**Indicadores atualizados (opção 9)**

```
Por situação:
  Aberta            5  ( 38.5%)
  Em análise        5  ( 38.5%)
  Concluída         3  ( 23.1%)
Pendências (abertas + em análise): 10
```

**Dados inválidos e registro não encontrado**

```
[ERRO] Cadastro não realizado:
  - 'descricao' parece conter dado pessoal (e-mail ou telefone)

[AVISO] Ocorrência '999' não encontrada.

[AVISO] Ocorrência concluída: a situação não pode mais ser alterada.
```

**Saída (opção 0)**

```
Opção: 0
Até logo! Obrigado por acompanhar as demandas da comunidade.
```

---

## ♿ Acessibilidade, inclusão e privacidade

**Acessibilidade**
- As mensagens começam com `[OK]`, `[ERRO]` ou `[AVISO]`, em texto e sem depender de cores, o que funciona com leitores de tela.
- Os menus são numerados, e as opções podem ser escolhidas pelo número ou pelo nome.
- As entradas aceitam acentos ou não, maiúsculas ou minúsculas, e códigos com ou sem zeros (`5` = `005`).
- Os erros explicam o motivo, em vez de só dizer "inválido".
- A opção 12 traz uma ajuda com o significado de cada situação.

**Inclusão**
- Acessibilidade é uma das quatro categorias, para que barreiras físicas (rampas, piso tátil, faixas) tenham o mesmo peso que as outras demandas.
- A fila de triagem segue a ordem de registro, sem passar ninguém na frente.

**Privacidade**
- O sistema **não guarda quem relatou**: nenhum campo é sobre pessoas.
- Os locais são genéricos ("Praça Central"), sem número de casa ou endereço exato.
- Uma regra de validação recusa descrições com e-mail ou com 8 ou mais dígitos seguidos (possível telefone ou documento).
- Todos os dados do repositório são fictícios.

---

## 📎 Links e Observações

### 🔗 Links do Projeto

* **[Vídeo de apresentação no YouTube](https://www.youtube.com/watch?v=0ncof68RPqY)**: demonstração do sistema (vídeo não listado).

### 🧠 Decisões Técnicas

- **Python puro, terminal:** o enunciado pede só conteúdos das Fases 1 a 3, sem bibliotecas externas.
- **CSV com `;`:** é fácil de editar em qualquer editor ou planilha, e o ponto e vírgula evita conflito com as vírgulas das descrições.
- **Um único arquivo `sistema.py`, dividido em seções numeradas:** configuração, validação, carregamento, estruturas, consultas, indicadores e telas. Isso facilita ler e apresentar o código.
- **Hierarquia e matriz calculadas na hora:** assim, elas nunca ficam desatualizadas depois de um cadastro ou de uma mudança de situação.
- **Dia simulado:** o sistema trabalha com "dia 30" em vez de datas reais, o que deixa os cálculos de tempo simples e reproduzíveis.
- **Uso de IA:** registrado em [`docs/uso_ia.md`](docs/uso_ia.md).

### 📢 Observações Gerais

* **Participação na Competição:** [X] Sim, aceitamos participar / [ ] Não vamos participar.

---

## 📌 Conclusões, limitações e aprendizados

**Conclusões**

Com estruturas simples (lista, dicionário, fila, pilha, hierarquia e matriz) e regras condicionais, o painel transforma relatos soltos em informação útil. Ele mostra o que está pendente, o que espera há mais tempo e onde os problemas se concentram. No conjunto simulado, os números apontam iluminação e acessibilidade como prioridades da Comunidade Vale Verde.

**Limitações**
- Os dados são fictícios e poucos (12 ocorrências): os números ilustram o funcionamento, mas não representam uma comunidade real.
- As alterações feitas no menu ficam só na memória e se perdem ao fechar o programa; o arquivo CSV não é regravado.
- O tempo é simulado em "dias", sem datas reais.
- A regra de privacidade detecta só padrões simples (e-mail e sequências de dígitos).
- Não há login, de modo que qualquer pessoa com acesso ao terminal pode alterar uma situação.
- Não há integração com prefeitura ou órgãos públicos.

**Aprendizados**
- A escolha da estrutura muda o código: com o dicionário, a busca por código ficou direta, e a fila garantiu a ordem justa de atendimento.
- Validar dados é tão importante quanto processá-los: os dois registros inconsistentes mostraram como um campo vazio ou um valor fora do padrão quebraria os indicadores.
- Uma expressão booleana bem montada evita repetir código, como no filtro que atende quatro tipos de consulta.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

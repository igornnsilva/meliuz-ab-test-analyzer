## Entregáveis

### Resumo consolidado

- [Planilha consolidada dos experimentos](outputs/experiment_tracker.csv)

### Parceiro A
- [Relatório PDF](reports/parceiro_a/relatorio.pdf)
- [Relatório HTML](reports/parceiro_a/relatorio.html)


### Parceiro B
- [Relatório PDF](reports/parceiro_b/relatorio.pdf)
- [Relatório HTML](reports/parceiro_b/relatorio.html)


### Parceiro C
- [Relatório PDF](reports/parceiro_c/relatorio.pdf)
- [Relatório HTML](reports/parceiro_c/relatorio.html)


# Analisador de Testes A/B de Cashback

Solução desenvolvida para o teste técnico de **Estágio de Growth AI-Native do Méliuz**.

O projeto recebe um dataset de teste A/B de cashback, valida a qualidade dos dados, calcula métricas de negócio, executa comparações estatísticas, recomenda qual variante deve ser escalada e registra o resultado em um arquivo consolidado.

A mesma aplicação processa os três datasets fornecidos sem alteração no código, sendo necessário apenas indicar o caminho do novo arquivo.

---

## Objetivo

Responder à seguinte pergunta:

> Dado este teste A/B, qual variante de cashback deve ser escalada para 100% do tráfego?

A solução considera tanto o impacto em crescimento quanto o impacto financeiro para o Méliuz.

---

## Principais funcionalidades

* Leitura parametrizada de arquivos CSV
* Validação automática do schema
* Conversão de valores monetários brasileiros
* Detecção de valores nulos, negativos e duplicados
* Verificação do alinhamento de datas entre os grupos
* Identificação de alterações na taxa de cashback durante o teste
* Cálculo de métricas financeiras e de crescimento
* Comparações estatísticas pareadas por data
* Motor de decisão automático e auditável
* Geração de gráficos
* Geração de relatórios HTML
* Exportação dos resultados para CSV
* Registro consolidado dos experimentos
* Testes automatizados com Pytest

---

## Arquitetura da solução

```text
meliuz-teste/
├── data/
│   ├── parceiro_a.csv
│   ├── parceiro_b.csv
│   └── parceiro_c.csv
│
├── outputs/
│   ├── experiment_tracker.csv
│   ├── parceiro_a_resumo_grupos.csv
│   ├── parceiro_a_comparacoes_estatisticas.csv
│   ├── parceiro_a_decisao.csv
│   └── ...
│
├── reports/
│   ├── parceiro_a/
│   │   ├── charts/
│   │   └── relatorio.html
│   ├── parceiro_b/
│   └── parceiro_c/
│
├── src/
│   ├── __init__.py
│   ├── charts.py
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── decision_engine.py
│   ├── metrics.py
│   ├── report_generator.py
│   ├── statistical_analysis.py
│   └── tracker.py
│
├── tests/
│   └── test_pipeline.py
│
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Responsabilidade de cada módulo

### `data_loader.py`

Responsável por:

* localizar o arquivo;
* validar as colunas obrigatórias;
* converter datas;
* converter valores monetários;
* preparar os campos para análise.

### `data_quality.py`

Responsável por verificar:

* duplicidades;
* valores nulos;
* valores negativos;
* valores zerados;
* cashback superior à comissão;
* datas desalinhadas entre grupos;
* estabilidade da taxa de cashback;
* presença de mais de um parceiro no arquivo.

### `metrics.py`

Responsável pelo cálculo das métricas de negócio.

### `statistical_analysis.py`

Responsável pelas comparações estatísticas pareadas entre as variantes e o grupo de controle.

### `decision_engine.py`

Responsável por transformar as métricas, os testes estatísticos e os alertas de qualidade em uma recomendação automática.

### `charts.py`

Responsável pela geração das visualizações.

### `report_generator.py`

Responsável pela criação do relatório HTML para apresentação gerencial.

### `tracker.py`

Responsável pelo registro consolidado dos testes analisados.

---

## Métricas utilizadas

### Receita líquida

```text
Receita líquida = comissão - cashback
```

Representa o valor que permanece para o Méliuz após a distribuição do cashback.

### Taxa de comissão

```text
Taxa de comissão = comissão / vendas totais
```

### Taxa de cashback

```text
Taxa de cashback = cashback / vendas totais
```

### Margem líquida

```text
Margem líquida = receita líquida / vendas totais
```

### Ticket médio

```text
Ticket médio = vendas totais / compradores
```

### Receita líquida por comprador

```text
Receita por comprador = receita líquida / compradores
```

A receita líquida foi utilizada como principal métrica financeira para o motor de decisão.

Compradores e vendas totais foram utilizados como métricas de crescimento.

---

## Limitação dos datasets

Os datasets não possuem o número de usuários expostos a cada variante.

Por esse motivo, não é possível calcular uma taxa de conversão tradicional:

```text
Conversão = compradores / usuários expostos
```

A análise compara compradores, vendas, receita líquida, ticket médio e margem entre as variantes.

---

## Metodologia estatística

As variantes possuem observações nas mesmas datas. Por isso, a solução utiliza comparações pareadas.

Cada dia de uma variante é comparado com o mesmo dia do grupo de controle.

Foram utilizados:

* teste t pareado;
* teste de Wilcoxon pareado;
* intervalo de confiança de 95%;
* lift percentual;
* diferença média diária.

O teste t pareado é utilizado como referência para a significância estatística.

O teste de Wilcoxon funciona como uma verificação adicional de robustez.

O nível de significância adotado é de 5%.

---

## Regras do motor de decisão

O motor pode retornar três situações principais.

### Escalar uma variante

Uma variante substitui o controle automaticamente quando apresenta aumento estatisticamente significativo de receita líquida.

### Manter e escalar o controle

Quando nenhuma variante melhora significativamente a receita líquida, o grupo de controle é mantido.

### Revisão necessária

A decisão automática é bloqueada quando existem problemas relevantes, como:

* tratamento instável;
* datas desalinhadas;
* duplicidades;
* valores negativos;
* dados incompletos;
* cashback superior à comissão.

Nessa situação, a solução pode indicar um grupo provisório, mas não trata o resultado como uma conclusão causal confiável.

---

## Resultados dos datasets fornecidos

### Parceiro A

**Decisão:** revisão necessária.

Os grupos apresentaram alterações na taxa de cashback durante o período do experimento.

Apesar de os grupos 2 e 3 apresentarem aumento em compradores e vendas, ambos reduziram a receita líquida.

Como os tratamentos não permaneceram estáveis, a solução bloqueia a decisão automática.

Caso fosse obrigatório escolher apenas com base nos resultados agregados, o Grupo 1 seria a escolha provisória por possuir a maior receita líquida total.

### Parceiro B

**Decisão:** escalar o Grupo 1.

O Grupo 1 apresentou:

* maior número de compradores;
* maior volume de vendas;
* maior receita líquida;
* melhor margem financeira;
* menor custo de cashback.

Os demais grupos apresentaram redução relevante de receita líquida.

### Parceiro C

**Decisão:** escalar o Grupo 1.

O Grupo 2 não apresentou melhoria estatisticamente significativa em compradores ou vendas.

Além disso, sua taxa de cashback consumiu praticamente toda a comissão, fazendo com que a receita líquida ficasse próxima de zero.

---

## Pré-requisitos

* Python 3.12 ou superior
* Pip
* Windows, Linux ou macOS

O projeto foi desenvolvido e testado com:

```text
Python 3.12.4
```

---

## Instalação

Clone o repositório:

```bash
git clone https://github.com/igornnsilva/meliuz-ab-test-analyzer.git
```

Entre na pasta:

```bash
cd meliuz-ab-test-analyzer
```

Crie o ambiente virtual:

### Windows

```powershell
py -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

---

## Como executar

### Parceiro A

```powershell
python main.py --file ".\data\parceiro_a.csv"
```

### Parceiro B

```powershell
python main.py --file ".\data\parceiro_b.csv"
```

### Parceiro C

```powershell
python main.py --file ".\data\parceiro_c.csv"
```

---

## Alterando o grupo de controle

O grupo de controle padrão é:

```text
Grupo 1
```

Para utilizar outro grupo:

```powershell
python main.py --file ".\data\parceiro_a.csv" --control "Grupo 2"
```

O grupo informado precisa existir no dataset.

---

## Utilização com um novo dataset

A aplicação pode processar qualquer novo arquivo que siga o mesmo schema:

| Coluna             | Descrição                     |
| ------------------ | ----------------------------- |
| Data               | Data da observação            |
| Grupos de usuários | Variante do teste             |
| Parceiro           | Nome do parceiro              |
| compradores        | Usuários únicos compradores   |
| comissão           | Comissão recebida pelo Méliuz |
| cashback           | Cashback distribuído          |
| vendas totais      | GMV diário                    |

Para executar:

```powershell
python main.py --file ".\data\novo_teste.csv"
```

Não é necessário alterar o código.

---

## Arquivos gerados

Para cada parceiro são gerados três arquivos CSV.

### Resumo consolidado

```text
outputs/parceiro_a_resumo_grupos.csv
```

Contém as métricas consolidadas de cada variante.

### Comparações estatísticas

```text
outputs/parceiro_a_comparacoes_estatisticas.csv
```

Contém:

* lift;
* médias;
* diferença média;
* intervalo de confiança;
* p-valor;
* significância;
* resultado do teste de Wilcoxon.

### Decisão

```text
outputs/parceiro_a_decisao.csv
```

Contém a recomendação final e sua justificativa.

---

## Relatórios HTML

Os relatórios gerenciais são salvos em:

```text
reports/parceiro_a/relatorio.html
reports/parceiro_b/relatorio.html
reports/parceiro_c/relatorio.html
```

No Windows, podem ser abertos com:

```powershell
Start-Process ".\reports\parceiro_a\relatorio.html"
```

Cada relatório possui:

* recomendação executiva;
* status da qualidade dos dados;
* resultados consolidados;
* comparações estatísticas;
* gráficos de compradores;
* gráficos de vendas;
* gráficos de receita líquida;
* gráfico da taxa de cashback;
* receita líquida consolidada.

---

## Planilha consolidada

Todos os experimentos são registrados em:

```text
outputs/experiment_tracker.csv
```

Cada linha representa um teste.

O arquivo contém, entre outras informações:

* nome do teste;
* descrição;
* parceiro;
* período;
* variantes;
* status dos dados;
* resultado;
* decisão;
* grupo recomendado;
* confiança;
* alertas;
* caminho do relatório.

Caso o mesmo teste seja executado novamente, seu registro é atualizado em vez de duplicado.

---

## Testes automatizados

Para executar:

```powershell
python -m pytest -v
```

Resultado esperado:

```text
7 passed
```

Os testes verificam:

* execução completa nos três datasets;
* decisões esperadas;
* detecção da instabilidade do Parceiro A;
* aprovação dos parceiros B e C;
* cálculo das métricas;
* funcionamento das comparações;
* atualização do tracker sem duplicidades.

---

## Abordagem AI-Native

A solução foi estruturada para ser utilizada por ferramentas como:

* Codex;
* Claude Code;
* Cursor;
* ChatGPT;
* Gemini.

Um usuário pode solicitar em linguagem natural:

```text
Analise o arquivo data/parceiro_b.csv e informe qual variante
de cashback deve ser escalada.
```

A ferramenta de IA pode executar:

```powershell
python main.py --file ".\data\parceiro_b.csv"
```

A IA funciona como interface de utilização e interpretação.

Os cálculos, validações estatísticas e regras de decisão permanecem implementados em Python de maneira determinística e auditável.

Essa separação reduz o risco de cálculos inventados ou respostas inconsistentes por parte de um modelo de linguagem.

---

## Decisões de arquitetura

A solução foi dividida em módulos para facilitar:

* manutenção;
* testes;
* reutilização;
* auditoria;
* inclusão de novas métricas;
* troca do formato de relatório;
* futura integração com Google Sheets;
* execução por agentes de IA.

O motor de decisão não depende de uma resposta livre de uma IA.

A recomendação é produzida por regras explícitas, que podem ser revisadas e alteradas conforme as prioridades do negócio.

---

## Possíveis evoluções

* integração direta com Google Sheets;
* interface web com Streamlit;
* análise bayesiana;
* correção para múltiplas comparações;
* cálculo de poder estatístico;
* estimativa de tamanho mínimo de amostra;
* configuração das regras por arquivo YAML;
* integração com banco de dados;
* execução automática em pipelines;
* geração de relatório em PDF;
* uso de uma LLM para produzir um resumo executivo complementar.

---

## Tecnologias utilizadas

* Python
* Pandas
* NumPy
* SciPy
* Matplotlib
* Pytest
* HTML
* CSS

---

## Autor

Igor Nascimento Silva

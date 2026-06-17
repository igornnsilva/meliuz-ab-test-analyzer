# Analisador de Testes A/B de Cashback

Solução reutilizável desenvolvida para o teste técnico de **Estágio de Growth AI-Native do Méliuz**.

O projeto recebe um dataset de teste A/B de cashback, valida a qualidade dos dados, calcula métricas financeiras e de crescimento, executa comparações estatísticas, recomenda qual grupo deve ser escalado e registra o resultado em uma planilha consolidada.

A mesma aplicação processa os três datasets fornecidos sem alterações no código. Para analisar um novo arquivo compatível, basta informar seu caminho no comando de execução.

---

## Entregáveis

### Resumo consolidado

* [Planilha consolidada dos experimentos](outputs/experiment_tracker.csv)

### Parceiro A

* [Relatório PDF](reports/parceiro_a/relatorio.pdf)
* [Relatório HTML](reports/parceiro_a/relatorio.html)

### Parceiro B

* [Relatório PDF](reports/parceiro_b/relatorio.pdf)
* [Relatório HTML](reports/parceiro_b/relatorio.html)

### Parceiro C

* [Relatório PDF](reports/parceiro_c/relatorio.pdf)
* [Relatório HTML](reports/parceiro_c/relatorio.html)

> Os arquivos PDF podem ser visualizados diretamente pelo GitHub. Para visualizar os relatórios HTML completamente renderizados, clone ou baixe o repositório e abra os arquivos localmente no navegador.

---

## Objetivo

Responder à seguinte pergunta de negócio:

> Dado este teste A/B, qual variante de cashback deve ser escalada para 100% do tráfego?

A solução considera simultaneamente:

* impacto financeiro para o Méliuz;
* comportamento de compradores;
* volume de vendas;
* custo de cashback;
* qualidade do experimento;
* significância estatística;
* incerteza dos resultados.

---

## Principais funcionalidades

* leitura parametrizada de arquivos CSV;
* validação automática do schema;
* conversão de valores monetários no padrão brasileiro;
* formatação monetária padronizada em todos os entregáveis;
* detecção de valores nulos, negativos e duplicados;
* identificação de valores zerados;
* verificação do alinhamento de datas entre os grupos;
* identificação de alterações na taxa de cashback durante o teste;
* cálculo de métricas financeiras e de crescimento;
* comparações estatísticas pareadas por data;
* cálculo de lift e intervalos de confiança;
* motor de decisão automático e auditável;
* geração de gráficos;
* geração de relatórios gerenciais em HTML;
* geração de relatórios gerenciais em PDF;
* exportação dos resultados individuais para CSV;
* registro consolidado dos experimentos;
* atualização do tracker sem duplicar testes;
* testes automatizados com Pytest;
* instruções específicas para utilização por agentes de IA.

---

## Arquitetura da solução

```text
meliuz-ab-test-analyzer/
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
│   ├── parceiro_b_resumo_grupos.csv
│   ├── parceiro_b_comparacoes_estatisticas.csv
│   ├── parceiro_b_decisao.csv
│   ├── parceiro_c_resumo_grupos.csv
│   ├── parceiro_c_comparacoes_estatisticas.csv
│   └── parceiro_c_decisao.csv
│
├── reports/
│   ├── parceiro_a/
│   │   ├── charts/
│   │   ├── relatorio.html
│   │   └── relatorio.pdf
│   ├── parceiro_b/
│   │   ├── charts/
│   │   ├── relatorio.html
│   │   └── relatorio.pdf
│   └── parceiro_c/
│       ├── charts/
│       ├── relatorio.html
│       └── relatorio.pdf
│
├── src/
│   ├── __init__.py
│   ├── charts.py
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── decision_engine.py
│   ├── formatters.py
│   ├── metrics.py
│   ├── pdf_report_generator.py
│   ├── report_generator.py
│   ├── statistical_analysis.py
│   └── tracker.py
│
├── tests/
│   └── test_pipeline.py
│
├── .gitignore
├── AGENTS.md
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Responsabilidade de cada módulo

### `data_loader.py`

Responsável por:

* localizar e carregar o arquivo;
* validar a extensão CSV;
* validar as colunas obrigatórias;
* converter datas;
* converter valores monetários;
* preparar os campos para análise;
* interromper a execução quando o dataset for inválido.

### `data_quality.py`

Responsável por verificar:

* duplicidades;
* valores nulos;
* valores negativos;
* valores zerados;
* cashback superior à comissão;
* datas desalinhadas entre grupos;
* estabilidade da taxa de cashback;
* presença de mais de um parceiro no mesmo arquivo;
* consistência do desenho experimental.

### `metrics.py`

Responsável pelo cálculo e pela consolidação das métricas de negócio.

### `statistical_analysis.py`

Responsável pelas comparações estatísticas pareadas entre cada variante e o grupo de controle.

### `decision_engine.py`

Responsável por transformar métricas, testes estatísticos e alertas de qualidade em uma recomendação automática e auditável.

### `charts.py`

Responsável pela geração das visualizações utilizadas nos relatórios.

### `formatters.py`

Responsável pela formatação padronizada de:

* valores monetários no padrão brasileiro;
* números inteiros com separadores de milhar.

Exemplo:

```text
R$ 404.711,00
```

### `report_generator.py`

Responsável pela criação do relatório gerencial em HTML.

### `pdf_report_generator.py`

Responsável pela criação do relatório gerencial em PDF, incluindo:

* resumo executivo;
* status da qualidade;
* decisão recomendada;
* métricas consolidadas;
* resultados estatísticos;
* gráficos;
* paginação e rodapé.

### `tracker.py`

Responsável pelo registro consolidado dos experimentos no arquivo:

```text
outputs/experiment_tracker.csv
```

Quando o mesmo parceiro e período são analisados novamente, o registro anterior é atualizado em vez de duplicado.

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

A receita líquida foi adotada como principal métrica financeira do motor de decisão.

Compradores e vendas totais são utilizados como métricas complementares de crescimento e volume.

---

## Limitação dos datasets

Os datasets não possuem o número de usuários expostos a cada variante.

Por esse motivo, não é possível calcular uma taxa de conversão tradicional:

```text
Conversão = compradores / usuários expostos
```

A solução compara diretamente:

* compradores;
* vendas totais;
* comissão;
* cashback;
* receita líquida;
* ticket médio;
* receita líquida por comprador;
* margem líquida.

Essa limitação é considerada durante a interpretação dos resultados.

---

## Metodologia estatística

As variantes possuem observações correspondentes nas mesmas datas. Por isso, a solução utiliza comparações pareadas.

Cada observação diária de uma variante é comparada com a observação do grupo de controle na mesma data.

Foram utilizados:

* teste t pareado;
* teste de Wilcoxon pareado;
* intervalo de confiança de 95%;
* lift percentual;
* diferença média diária;
* direção do efeito;
* quantidade de pares analisados.

O teste t pareado é utilizado como referência principal para significância estatística.

O teste de Wilcoxon é utilizado como verificação adicional de robustez.

O nível de significância adotado é de 5%.

Um aumento de média não é tratado automaticamente como evidência suficiente. A solução também considera o p-valor, o intervalo de confiança e a qualidade do experimento.

---

## Regras do motor de decisão

O motor pode retornar três situações principais.

### Escalar uma variante

Uma variante pode substituir o controle quando apresenta melhora estatisticamente significativa de receita líquida e o intervalo de confiança indica efeito positivo.

### Manter e escalar o controle

Quando nenhuma variante melhora significativamente a receita líquida, o grupo de controle é mantido.

### Revisão necessária

A decisão automática é bloqueada quando existem problemas relevantes, como:

* tratamento instável;
* datas desalinhadas;
* duplicidades;
* valores negativos;
* dados incompletos;
* cashback superior à comissão;
* inconsistências no desenho experimental.

Nessa situação, a solução pode indicar um grupo provisório, mas não trata o resultado como uma conclusão causal confiável.

---

## Resultados dos datasets fornecidos

### Parceiro A

**Decisão:** revisão necessária.

Os grupos apresentaram alterações na taxa de cashback durante o período do experimento.

Apesar de os grupos 2 e 3 apresentarem aumento em compradores e vendas, ambos reduziram a receita líquida.

Como os tratamentos não permaneceram estáveis, a solução bloqueia a decisão automática.

Caso fosse obrigatório escolher somente com base nos resultados agregados, o Grupo 1 seria a escolha provisória por possuir a maior receita líquida total.

### Parceiro B

**Decisão:** escalar o Grupo 1.

O Grupo 1 apresentou:

* maior número de compradores;
* maior volume de vendas;
* maior receita líquida;
* melhor margem financeira;
* menor custo de cashback.

Os grupos com cashback maior apresentaram reduções estatisticamente significativas de receita líquida e não devem ser escalados.

### Parceiro C

**Decisão:** escalar o Grupo 1.

O Grupo 2 não apresentou melhoria estatisticamente significativa em compradores ou vendas.

Além disso, sua taxa de cashback consumiu praticamente toda a comissão, fazendo com que a receita líquida ficasse próxima de zero.

---

## Pré-requisitos

* Python 3.12.x;
* Pip;
* Git para clonar o repositório.

Ambiente principal utilizado no desenvolvimento e na validação:

```text
Windows 11
Python 3.12.4
```

O projeto também pode ser executado em Linux ou macOS com os comandos equivalentes de criação e ativação do ambiente virtual.

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

### Windows

Crie o ambiente virtual:

```powershell
py -3.12 -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux e macOS

Crie o ambiente virtual:

```bash
python3.12 -m venv .venv
```

Ative o ambiente:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> A pasta `.venv` não é versionada. Cada usuário deve criar seu próprio ambiente virtual após clonar o repositório.

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

Em Linux e macOS, utilize barras normais:

```bash
python main.py --file "./data/parceiro_b.csv"
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

A aplicação pode processar qualquer novo arquivo que siga o mesmo schema.

| Coluna               | Descrição                     |
| -------------------- | ----------------------------- |
| `Data`               | Data da observação            |
| `Grupos de usuários` | Grupo ou variante do teste    |
| `Parceiro`           | Nome do parceiro              |
| `compradores`        | Quantidade de compradores     |
| `comissão`           | Comissão recebida pelo Méliuz |
| `cashback`           | Cashback distribuído          |
| `vendas totais`      | Volume financeiro diário      |

Para executar:

```powershell
python main.py --file ".\data\novo_teste.csv"
```

Não é necessário alterar o código para trocar o dataset.

---

## Arquivos CSV gerados

Para cada parceiro são gerados três arquivos individuais.

### Resumo consolidado

```text
outputs/<parceiro>_resumo_grupos.csv
```

Contém as métricas consolidadas de cada grupo.

### Comparações estatísticas

```text
outputs/<parceiro>_comparacoes_estatisticas.csv
```

Contém:

* lift;
* médias diárias;
* diferença média;
* intervalo de confiança;
* p-valor do teste t pareado;
* p-valor do teste de Wilcoxon;
* indicação de significância;
* direção do efeito.

### Decisão

```text
outputs/<parceiro>_decisao.csv
```

Contém a recomendação final, o grupo recomendado, o nível de confiança e a justificativa.

---

## Relatórios HTML e PDF

Para cada parceiro são gerados dois relatórios gerenciais:

```text
reports/<parceiro>/relatorio.html
reports/<parceiro>/relatorio.pdf
```

Exemplo:

```text
reports/parceiro_a/relatorio.html
reports/parceiro_a/relatorio.pdf
```

Os relatórios apresentam:

* identificação do parceiro;
* período do experimento;
* grupo de controle;
* status da qualidade dos dados;
* decisão recomendada;
* grupo recomendado;
* nível de confiança;
* justificativa executiva;
* alertas de qualidade;
* métricas consolidadas;
* comparações estatísticas;
* gráficos de compradores;
* gráficos de vendas;
* gráficos de receita líquida;
* gráfico da taxa de cashback;
* receita líquida total.

No Windows, os arquivos podem ser abertos com:

```powershell
Start-Process ".\reports\parceiro_a\relatorio.html"
Start-Process ".\reports\parceiro_a\relatorio.pdf"
```

---

## Planilha consolidada

Todos os experimentos são registrados em:

```text
outputs/experiment_tracker.csv
```

Cada linha representa um teste analisado.

O arquivo contém, entre outras informações:

* identificador do teste;
* nome;
* descrição;
* parceiro;
* data inicial;
* data final;
* grupos analisados;
* quantidade de grupos;
* status dos dados;
* resultado;
* decisão;
* grupo recomendado;
* indicação de escala automática;
* confiança;
* alertas;
* caminho do relatório HTML;
* caminho do relatório PDF;
* data e hora da análise.

As colunas de relatórios são:

```text
relatorio
relatorio_pdf
```

Caso o mesmo parceiro e período sejam executados novamente, o registro anterior é atualizado em vez de duplicado.

O arquivo é salvo em `UTF-8 com BOM`, facilitando sua abertura no Excel e em outros aplicativos de planilha.

---

## Testes automatizados

Execute:

```powershell
python -m pytest -v
```

Resultado esperado:

```text
8 passed
```

Os testes verificam:

* execução completa nos três datasets;
* decisões esperadas;
* detecção da instabilidade do Parceiro A;
* aprovação dos parceiros B e C;
* cálculo das métricas;
* funcionamento das comparações estatísticas;
* atualização do tracker sem duplicidades;
* formatação monetária no padrão brasileiro.

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

Os cálculos, validações estatísticas e regras de decisão permanecem implementados em Python de forma determinística e auditável.

Essa separação reduz o risco de cálculos inventados ou respostas inconsistentes por parte do modelo de linguagem.

O arquivo [`AGENTS.md`](AGENTS.md) contém instruções específicas para agentes de IA, incluindo:

* comandos de execução;
* regras de interpretação;
* validação dos artefatos;
* execução obrigatória dos testes;
* indicação obrigatória dos relatórios HTML e PDF;
* indicação obrigatória da planilha consolidada;
* formato esperado da resposta final.

---

## Decisões de arquitetura

A solução foi dividida em módulos para facilitar:

* manutenção;
* testes;
* reutilização;
* auditoria;
* inclusão de novas métricas;
* troca ou inclusão de formatos de relatório;
* futura integração com Google Sheets;
* execução por agentes de IA.

O motor de decisão não depende de uma resposta livre de uma IA.

A recomendação é produzida por regras explícitas, que podem ser revisadas e alteradas conforme as prioridades do negócio.

---

## Limitações estatísticas

A versão atual possui algumas limitações que devem ser consideradas:

* ausência do número de usuários expostos;
* impossibilidade de calcular conversão tradicional;
* ausência de correção para múltiplas comparações;
* ausência de cálculo formal de poder estatístico;
* ausência de estimativa automática de tamanho mínimo de amostra;
* possível autocorrelação entre observações temporais;
* análise baseada em dados agregados por dia.

Essas limitações não impedem a utilização da solução nos datasets fornecidos, mas devem ser consideradas antes de uma aplicação em produção.

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
* execução automática em pipelines de CI/CD;
* testes adicionais para datasets inválidos;
* publicação dos relatórios HTML com GitHub Pages;
* resumo executivo complementar produzido por uma LLM.

---

## Tecnologias utilizadas

* Python;
* Pandas;
* NumPy;
* SciPy;
* Matplotlib;
* ReportLab;
* Pytest;
* HTML;
* CSS;
* Git;
* GitHub.

---

## Autor

**Igor Nascimento Silva**

GitHub: [@igornnsilva](https://github.com/igornnsilva)

# Instruções para agentes de IA

Este repositório contém uma solução reutilizável para análise de testes A/B de cashback.

O agente deve utilizar o pipeline existente como fonte principal dos cálculos, das métricas, das validações de qualidade e das decisões. Não deve substituir a execução do projeto por cálculos manuais ou conclusões improvisadas.

## Objetivo principal

Ao receber um pedido em linguagem natural para analisar um dataset, o agente deve:

1. identificar o arquivo CSV informado;
2. verificar se o arquivo existe;
3. executar o pipeline existente;
4. verificar a qualidade dos dados;
5. interpretar as métricas de negócio;
6. interpretar os testes estatísticos;
7. informar qual grupo deve ser escalado;
8. explicar alertas, limitações ou problemas experimentais;
9. verificar a geração do relatório HTML;
10. verificar a geração do relatório PDF;
11. verificar a atualização da planilha consolidada em CSV;
12. executar os testes automatizados;
13. apresentar todos os artefatos gerados na resposta final.

A análise só é considerada concluída depois que o relatório HTML, o relatório PDF e o arquivo `outputs/experiment_tracker.csv` forem gerados ou atualizados e informados na resposta final.

## Comando principal

```bash
python main.py --file "CAMINHO_DO_DATASET"
```

Exemplo no Windows:

```powershell
python main.py --file ".\data\parceiro_b.csv"
```

O grupo de controle padrão é `Grupo 1`.

Para utilizar outro grupo como controle:

```powershell
python main.py --file ".\data\parceiro_a.csv" --control "Grupo 2"
```

## Ambiente Python

### Windows

Na raiz do projeto, ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Execute o pipeline com:

```powershell
python main.py --file ".\data\arquivo.csv"
```

Caso a política de execução do PowerShell bloqueie a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux e macOS

```bash
source .venv/bin/activate
python main.py --file "./data/arquivo.csv"
```

### Ambiente virtual ausente ou inválido

Não altere manualmente o arquivo `.venv/pyvenv.cfg`.

Se o ambiente virtual estiver ausente ou inválido, recrie-o utilizando uma instalação válida do Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se não houver uma instalação válida do Python disponível, interrompa a execução e informe claramente o problema. Não aplique alterações temporárias no `pyvenv.cfg`.

## Regras obrigatórias

* Não alterar o código apenas para trocar o dataset.
* Não criar lógica específica para um parceiro.
* Não modificar os datasets originais.
* Não realizar cálculos financeiros manualmente quando o pipeline puder executá-los.
* Não escolher um vencedor ignorando os alertas de qualidade.
* Não considerar um aumento como comprovado apenas porque a média é maior.
* Verificar p-valor, intervalo de confiança e tamanho do efeito.
* Priorizar a receita líquida como métrica financeira principal.
* Utilizar compradores e vendas totais como métricas complementares de crescimento.
* Não calcular taxa de conversão, pois os datasets não possuem o número de usuários expostos.
* Quando o tratamento for instável, informar que não existe uma conclusão causal confiável.
* Não alterar uma decisão gerada pelo motor sem explicar claramente o motivo.
* Não inventar métricas, resultados, arquivos ou caminhos.
* Não afirmar que um artefato foi criado antes de verificar sua existência.
* Não declarar que a solução está funcionando caso algum teste automatizado falhe.
* Não adicionar credenciais, tokens, segredos ou dados pessoais ao repositório.
* Utilizar caminhos relativos ao repositório na resposta final.
* Não apresentar caminhos absolutos específicos da máquina, como `C:\Users\...` ou `G:\...`, como caminho principal dos entregáveis.

## Métricas principais

O pipeline utiliza, entre outras, as seguintes métricas:

* compradores;
* vendas totais;
* comissão;
* cashback;
* receita líquida;
* ticket médio;
* receita por comprador;
* taxa de comissão;
* taxa de cashback;
* margem líquida.

A receita líquida é calculada como:

```text
receita líquida = comissão - cashback
```

A receita líquida é a métrica financeira principal do motor de decisão.

Compradores e vendas totais devem ser apresentados como métricas complementares para avaliar o impacto sobre crescimento e volume.

## Interpretação estatística

As comparações são realizadas de forma pareada por data.

Ao interpretar uma variante, o agente deve considerar:

* lift percentual;
* diferença média diária;
* teste t pareado;
* teste de Wilcoxon;
* p-valor;
* intervalo de confiança de 95%;
* direção do efeito;
* qualidade do desenho experimental.

Um resultado não deve ser declarado como comprovado apenas por apresentar uma média superior.

Quando o intervalo de confiança incluir zero ou o resultado não for estatisticamente significativo, o agente deve deixar clara a incerteza.

## Interpretação das decisões

### `ESCALAR`

O grupo recomendado pode receber maior participação de tráfego segundo as regras implementadas no motor de decisão.

O agente deve explicar:

* por que o grupo foi recomendado;
* quais métricas sustentam a decisão;
* quais variantes não devem ser escaladas;
* se há riscos ou limitações relevantes.

### `REVISÃO NECESSÁRIA`

Existe algum problema de qualidade, consistência ou desenho experimental que impede uma decisão automática confiável.

Nesse caso, o agente deve:

* explicar o problema encontrado;
* informar que não existe conclusão causal definitiva;
* deixar claro que um grupo provisório não representa um vencedor comprovado;
* recomendar revisão ou repetição do experimento quando aplicável.

## Arquivos gerados

Para cada execução, o pipeline produz arquivos como:

```text
outputs/<parceiro>_resumo_grupos.csv
outputs/<parceiro>_comparacoes_estatisticas.csv
outputs/<parceiro>_decisao.csv
```

Também são gerados os relatórios:

```text
reports/<parceiro>/relatorio.html
reports/<parceiro>/relatorio.pdf
```

Os gráficos ficam armazenados em:

```text
reports/<parceiro>/charts/
```

O registro consolidado dos experimentos é criado ou atualizado em:

```text
outputs/experiment_tracker.csv
```

O tracker deve registrar, entre outras informações:

* parceiro;
* período;
* variantes;
* status dos dados;
* resultado;
* decisão;
* grupo recomendado;
* confiança;
* alertas;
* caminho do relatório HTML;
* caminho do relatório PDF.

## Verificação obrigatória dos artefatos

Antes de finalizar a resposta, verifique se existem:

```text
reports/<parceiro>/relatorio.html
reports/<parceiro>/relatorio.pdf
outputs/experiment_tracker.csv
```

No PowerShell, a verificação pode ser feita com:

```powershell
Test-Path ".\reports\<parceiro>\relatorio.html"
Test-Path ".\reports\<parceiro>\relatorio.pdf"
Test-Path ".\outputs\experiment_tracker.csv"
```

Os três comandos devem retornar:

```text
True
```

Caso algum arquivo não exista:

* informe qual artefato está ausente;
* não forneça um link inexistente;
* não declare que a análise foi concluída integralmente;
* tente gerar novamente o artefato utilizando o pipeline.

## Validação automatizada

Antes de concluir, execute:

```powershell
python -m pytest -v
```

O resultado esperado atualmente é:

```text
8 passed
```

Caso algum teste falhe:

* informe a falha;
* não declare que a solução está funcionando corretamente;
* não apresente a validação como concluída;
* corrija o problema antes de finalizar, quando a solicitação permitir alterações.

## Formato obrigatório da resposta final

Após executar qualquer análise, a resposta final deve apresentar obrigatoriamente todos os campos abaixo.

Nunca finalize uma análise omitindo a planilha consolidada, o relatório HTML ou o relatório PDF.

```text
Parceiro:
Período:
Status da qualidade:
Grupo de controle:
Grupo recomendado:
Decisão:
Confiança:

Principais impactos:
Alertas:

Relatório HTML:
Relatório PDF:
Planilha consolidada:

Validação:
```

### Regras para cada campo

#### Parceiro

Informar exatamente o parceiro presente no dataset.

#### Período

Informar a primeira e a última data do experimento.

#### Status da qualidade

Informar o status retornado pelo pipeline e resumir eventuais problemas.

#### Grupo de controle

Informar o grupo utilizado como controle na execução.

#### Grupo recomendado

Informar o grupo recomendado pelo motor de decisão.

Quando possível, também informar o tratamento associado, como a taxa aproximada de cashback.

#### Decisão

Utilizar a decisão gerada pelo pipeline, como:

```text
ESCALAR
```

ou:

```text
REVISÃO NECESSÁRIA
```

#### Confiança

Informar o nível de confiança retornado pelo motor de decisão.

#### Principais impactos

Apresentar, de maneira objetiva:

* efeito sobre receita líquida;
* efeito sobre vendas;
* efeito sobre compradores;
* significância estatística;
* comparação com o grupo de controle.

Não inventar percentuais. Utilizar somente valores produzidos pelo pipeline.

#### Alertas

Apresentar os alertas de qualidade e as limitações da análise.

Caso não existam alertas:

```text
Nenhum problema relevante de qualidade foi encontrado.
```

#### Relatório HTML

Apresentar sempre o caminho relativo:

```text
reports/<parceiro>/relatorio.html
```

#### Relatório PDF

Apresentar sempre o caminho relativo:

```text
reports/<parceiro>/relatorio.pdf
```

#### Planilha consolidada

Apresentar sempre:

```text
outputs/experiment_tracker.csv
```

A planilha consolidada deve ser mencionada mesmo quando não houver alteração visual evidente, pois é um dos entregáveis obrigatórios da solução.

#### Validação

Informar o resultado real da suíte de testes:

```text
pytest executado com sucesso: 8 passed.
```

Não informar `8 passed` sem executar os testes na sessão atual.

## Modelo de resposta final

```text
Parceiro: Parceiro B
Período: 01/05/2011 a 30/06/2011
Status da qualidade: APROVADO, sem alertas relevantes
Grupo de controle: Grupo 1
Grupo recomendado: Grupo 1
Decisão: ESCALAR
Confiança: ALTA

Principais impactos:
O Grupo 1 apresentou a melhor receita líquida. As variantes
com cashback maior apresentaram redução de receita líquida,
vendas e compradores em comparação com o controle.

Alertas:
Nenhum problema relevante de qualidade foi encontrado.

Relatório HTML:
reports/parceiro_b/relatorio.html

Relatório PDF:
reports/parceiro_b/relatorio.pdf

Planilha consolidada:
outputs/experiment_tracker.csv

Validação:
pytest executado com sucesso: 8 passed.
```

## Alterações no código

Ao implementar melhorias:

1. preservar a compatibilidade com os três datasets oficiais;
2. manter a entrada parametrizada por arquivo;
3. evitar lógica específica para um parceiro;
4. manter as decisões auditáveis;
5. atualizar ou adicionar testes;
6. executar toda a suíte de testes;
7. conferir a geração dos arquivos CSV;
8. conferir a geração do HTML;
9. conferir a geração do PDF;
10. conferir a atualização do tracker;
11. atualizar o README quando a funcionalidade pública mudar;
12. não adicionar credenciais ao repositório.

## Condição de conclusão

Uma análise só pode ser declarada concluída quando:

* o pipeline tiver sido executado;
* a qualidade dos dados tiver sido verificada;
* a decisão tiver sido interpretada;
* o relatório HTML existir;
* o relatório PDF existir;
* o tracker consolidado existir e estiver atualizado;
* os testes automatizados tiverem sido executados;
* a resposta final apresentar os caminhos relativos dos três entregáveis.

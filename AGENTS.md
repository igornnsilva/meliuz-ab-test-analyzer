# Instruções para agentes de IA

Este repositório contém uma solução reutilizável para análise de testes A/B de cashback.

## Objetivo principal

Ao receber um pedido em linguagem natural para analisar um dataset, o agente deve:

1. identificar o arquivo CSV informado;
2. executar o pipeline existente;
3. verificar a qualidade dos dados;
4. interpretar as métricas e os testes estatísticos;
5. informar qual grupo deve ser escalado;
6. indicar limitações ou alertas;
7. apontar onde o relatório e os arquivos de saída foram gerados.

## Comando principal

```bash
python main.py --file "CAMINHO_DO_DATASET"
```

Exemplo no Windows:

```powershell
python main.py --file ".\data\parceiro_b.csv"
```

O grupo de controle padrão é `Grupo 1`.

Para alterar o grupo de controle:

```powershell
python main.py --file ".\data\parceiro_a.csv" --control "Grupo 2"
```

## Regras importantes

* Não alterar o código apenas para trocar o dataset.
* Não realizar cálculos financeiros manualmente quando o pipeline puder executá-los.
* Não escolher um vencedor ignorando os alertas de qualidade.
* Não considerar um aumento como comprovado apenas porque a média é maior.
* Verificar o p-valor, o intervalo de confiança e o tamanho do efeito.
* Priorizar a receita líquida como métrica financeira principal.
* Usar compradores e vendas totais como métricas de crescimento.
* Não calcular taxa de conversão, pois os datasets não possuem usuários expostos.
* Quando o tratamento for instável, informar que não existe uma conclusão causal confiável.
* Não modificar os datasets originais.

## Arquivos gerados

Para cada execução, o pipeline produz:

```text
outputs/<parceiro>_resumo_grupos.csv
outputs/<parceiro>_comparacoes_estatisticas.csv
outputs/<parceiro>_decisao.csv
reports/<parceiro>/relatorio.html
```

O registro consolidado é atualizado em:

```text
outputs/experiment_tracker.csv
```

## Interpretação das decisões

### `ESCALAR`

O grupo recomendado pode receber 100% do tráfego segundo as regras implementadas.

### `REVISÃO NECESSÁRIA`

Existe algum problema de qualidade ou de desenho experimental que impede uma decisão automática confiável.

Nesse caso, o agente deve explicar o problema e deixar claro que o grupo provisório não representa uma conclusão causal definitiva.

## Formato esperado da resposta

Ao finalizar uma análise, apresentar:

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
Caminho do relatório:
```

## Validação antes de concluir

Execute:

```powershell
python -m pytest -v
```

O resultado esperado atualmente é:

```text
7 passed
```

Se algum teste falhar, não declarar que a solução está funcionando corretamente antes de corrigir o problema.

## Alterações no código

Ao implementar melhorias:

1. preservar a compatibilidade com os três datasets;
2. manter a entrada parametrizada;
3. evitar lógica específica para um parceiro;
4. adicionar ou atualizar testes;
5. executar toda a suíte de testes;
6. não adicionar credenciais ao repositório;
7. manter relatórios e decisões auditáveis.

## Ambiente Python

No Windows, prefira executar o projeto com:

```powershell
python main.py --file ".\data\arquivo.csv"
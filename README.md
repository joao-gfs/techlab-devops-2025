# Agente de IA para Rateio de Custos

Este repositório contém a submissão do código referente ao **Desafio Agent (Devops)** do **TechLab CEU 2025**.

## Desafio
Criar um Agente de Inteligência Artificial que faça o rateio de custos de uma empresa com base em planilhas de gastos.

Esse tipo de planilha comumente não é padronizado e pode sofrer alterações rápidas em sua estrutura, o que desfavorece o uso de computação tradicional por sua falta de flexibilidade.

O Agente precisa ser dinâmico e capaz de lidar com diferentes estruturas sem necessidade de refazer partes do código a cada alteração nas entradas.

## Estrutura do Projeto

```
root/
├── data/                   # Dados de entrada e saída
│   ├── input/              # Planilhas de entrada
│   └── output/             # Planilhas de saída
├── .env                    # Variáveis de ambiente
├── requirements.py         # Dependências do projeto
├── main.py                 # Execução principal do programa
├── settings.py             # Configurações do projeto
├── agent_builder.py        # Inicialização e configuração dos agentes
├── graph.py                # Construção dos grafos de agentes
├── tools.py                # Ferramentas dos utilizadas pelos agentes
├── utils.py                # Funções auxiliares reutilizáveis
└── README.md               # Documentação do projeto
```

## Ferramentas e Tecnologias

 - **Python 3.10+** - Linguagem do projeto
 - **Pandas** - Manipulação de dados
 - **llama-3.3-70b-versatile** - Modelo de LLM usado como motor do projeto
 - **LangGraph** - Framework de Agentes IA
 - **Git** - Controle de versão

 ## Arquitetura

A arquitetura é um pipeline de agentes simples e especializados, em que cada um tem uma função bem definida na manipulação de dados.

Os agentes LangGraph não conseguem trabalhar com tipos complexos como `Dataframe` do pandas. Por isso, é utilizado um cache em forma de dicionário que contém os dataframes provenientes das planilhas. 

Todas as interações com os dados são intermediadas pelas `tools`, que acessam esse dicionário, extraem ou operam as ações necessárias, e retornam apenas `strings`. A chaves para cada dataframe são os nomes das planilhas reais.

### Tools

As tools são utilizadas pelos agentes para consultar e modificar os dataframes.

- `sheet_overview`: mostra os nomes das colunas e uma linha de exemplo da planilha.

- `remove_columns`: remove colunas especificadas de uma planilha.

- `merge_files`: une dois arquivos com base em colunas correspondentes informadas.

- `rename_column`: renomeia uma coluna em uma planilha.

- `add_columns`: soma os valores de colunas e cria uma nova chamada `Total`.

### Agentes
**1. Identifier:** Recebe os nomes das planilhas e pode consultar o nomes das colunas e uma amostra dos dados. Sua saída é uma resposta identificando quais colunas são relevantes em cada arquivo e qual é a planilha principal, ou seja, a que tem o cadastro de todos os funcionários.

**Exemplo de saída:**
```
Dados Colaboradores.xlsx (MAIN FILE)
columns to be kept: ['Nome', 'CPF', 'Departamento', 'Salario'], remove all others

Beneficio 2 - Gympass.xlsx
columns to be kept: ['Assinante', 'Documento', 'Valor Mensal'], remove all others

Beneficio 1 - Unimed.xlsx
columns to be kept: ['Beneficiário', 'CPF', 'Total'], remove all others

Ferramenta 2 - Google workspace.xlsx
columns to be kept: ['Assinante', 'Documento', 'Valor Mensal'], remove all others

Ferramenta 1 - Github.xlsx
columns to be kept: ['Assinante', 'Documento', 'Valor Mensal'], remove all others
```

**2. Eraser:** Recebe a saída do **Identifier** e apaga as colunas que não estão listadas.

**3. Renamer:** Recebe a saída do **Identifier** e renomeia as colunas de valor monetário de acordo com o assunto da planilha.

**4. Merger:** Faz a junção das planilhas usando as colunas de identificação dos funcionários. Essa junção é guardada no arquivo marcado com `(MAIN FILE)` pelo **Identifier**. Ao finalizar, responde com o nome desse arquivo:

**Exemplo de saída:**
```
Dados Colaboradores.xlsx
```
**5. Final Eraser**: Recebe a saída do Merger e remove colunas redundantes que permanecem no DataFrame após a junção.

Isso é necessário porque a função merge do pandas mantém todas as colunas usadas na junção, mesmo que elas tenham o mesmo nome e conteúdo. Por exemplo, ao fazer um merge pelas colunas `'Nome'` e `'Assinante'`, o pandas pode manter ambas no DataFrame final, mesmo que seus valores sejam equivalentes. O Final Eraser garante que essas duplicações sejam eliminadas.

**6. Adder**: Recebe a saída do **Merger**, consulta quais colunas têm valor monetário no arquivo principal e as soma, criando uma nova coluna **Total**.


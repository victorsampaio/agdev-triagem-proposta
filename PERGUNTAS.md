# Perguntas técnicas

Respostas com base no que já fiz. Em cada uma, separo o que foi feito por mim e o que foi da equipe. Quando não tenho experiência, digo isso.

## 1. GitHub em equipe

> Conte uma situação em que vários desenvolvedores mexiam no mesmo repositório: como eram organizadas as branches e a revisão de código, como vocês resolviam conflitos e quem cuidava das permissões e das versões publicadas.

**Contexto:** Projeto: LabSpace | Petrobras, Empresa: Global Hitss, Período: Atualmente, Equipe com 4 integrantes.

**Branches e revisão de código:** Utilizamos o workflow padrão do GitHub com branches: main, develop, hotfix, feature. Os pull requests são realizados de acordo com as funcionalidades liberadas ou as correções executadas. Os pull requests passam antes por uma revisão do Arquiteto e de um desenvolvedor.

**Conflitos:** A resolução de conflitos é sempre alinhada com os desenvolvedores envolvidos nas funcionalidades em que afetou o código. Dessa forma é possível verificar os impactos e a melhor solução para o conflito. Houve uma situação com 2 desenvolvedores atuando na mesma tela, porém em funcionalidades diferentes, mas que acabava impactando uma mesma classe. Ao realizar o Merge e Pull Request foram identificados alguns pontos de conflito. Após analisar verificou-se que ambas as alterações entrariam no merge. Em uma breve reunião com os desenvolvedores foi dialogado sobre o desenvolvimento e os impactos, porém houve a decisão de manter as duas alterações após identificar que não haveria impacto nas demais funcionalidades.

**Permissões e versões publicadas:** Em geral quem cuida das versões é o arquiteto ou DevOps também podendo ser a própria esteira de produção por meio de configuração das Actions, onde o desenvolvedor informa as Labels para serem geradas as marcações e as versões, builds e as publicações.

**O que foi meu e o que foi da equipe:**  

## 2. Google Cloud

> Você já trabalhou com Google Cloud? O que publicou ou configurou lá? Como tratou credenciais, segredos e custo?

**Experiência:** Não tenho experiência com Google Cloud.

**Credenciais e segredos:** 

**Custo:**  

**O que foi meu e o que foi da equipe:**  

## 3. Apps Script

> Você já fez automação com Google Apps Script ou Google Sheets? Dê um exemplo real.

**Exemplo:** Não tenho experiência com Apps Script.

**O que foi meu e o que foi da equipe:**  

## 4. APIs REST

> Você já integrou APIs como Asana, Slack, Gmail ou Pipedrive? Como lidou com autenticação, limite de chamadas e erros?

**Integração:** Já realizei integrações com API Rest, trabalhando com requisições e os verbos do Rest e Restful, porém não realizei integrações com as APIs citadas.

**Autenticação:** Algumas APIs tratávamos utilizando OAuth.

**Limite de chamadas:** 

**Erros:** Os principais erros eram tratados informando em tela o que havia ocorrido e gerando logs para as devidas tratativas e correções.

**O que foi meu e o que foi da equipe:** 

## 5. LLM

> Você já construiu um agente ou automação com LLM? Usou Claude, skills ou MCP? O que funcionou, o que deu errado e como você corrigiu?

**Experiência anterior:** Atualmente estou iniciando e aprofundando os conhecimentos com IA. Tenho estudado e estou aplicando em um caso para o condomínio onde resido. A intenção é fazer o acompanhamento e a gestão financeira, verificando o histórico financeiro desde 2021, buscando possíveis fraudes financeiras e transações financeiras que necessitem de atenção para encaminhar para auditoria. Controle financeiro, gestão de fluxo de caixa, acompanhamento de evolução de saldo mensais e anuais. Análise e previsão financeira para os próximos meses.

**Neste teste:** construí a skill `triagem-proposta` para o Claude Code. Após a leitura dos requisitos do teste, realizei um levantamento de dúvidas e questões a serem esclarecidas. Estabeleci premissas a serem adotadas para cada cenário. Analisei a tabela de regras proposta e as visualizei como uma "Tabela Verdade" onde cada regra seria um critério de aceite para os Status propostos (SEGUE, REVISÃO HUMANA e RECUSADA). Funcionou deixar a decisão no código e o Claude só na conversa: na validação, ele se recusou a ignorar a R2 quando pedi e não inventou um campo que faltava. Deu errado a primeira versão do `SKILL.md`, que mandava passar o JSON dentro do comando; o Claude Code bloqueia isso. Corrigi fazendo a skill gravar a proposta num arquivo antes de rodar o script. Detalhes em `docs/validacao-claude-code.md`.

**O que foi meu e o que foi da equipe:** Busquei gerar toda a parte de lógica, fluxo, e decisões bem claras para que a implementação fosse realizada pela IA. Fui realizando a criação de cada passo e verificando de acordo com a arquitetura proposta, e validando cada ação após analisar e verificar se o comportamento era o esperado.

## 6. Docker

> Você já usou Docker? Já subiu uma aplicação em contêiner? Como trata senhas e chaves?

**Experiência:** Utilizo o docker e alguns contêineres no dia a dia de forma a simular alguns cenários e ambientes no qual preciso. Em geral utilizo de forma local para realização de integração com algum banco de dados local ou alguma camada de serviço local.

**Senhas e chaves:** No uso local, as senhas e chaves ficam no arquivo .env que é lido pelo Docker - docker compose.  

**O que foi meu e o que foi da equipe:**

## 7. Django

> Você já trabalhou com Django? O que construiu?

**Experiência:**  Não tenho experiência profissional com Django. Já estudei em um curso há algum tempo. 

**O que foi meu e o que foi da equipe:**

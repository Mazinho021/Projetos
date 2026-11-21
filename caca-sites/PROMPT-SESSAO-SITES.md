# Prompt para a sessão de sites

Copie tudo o que está abaixo da linha e cole na sessão que faz os sites.

---

Quero montar um gerador de **prévias de site** para vender sites a pequenas empresas que ainda não têm um. Outra sessão já caça essas empresas no Google e gera uma **ficha JSON de cada uma**. Sua parte é transformar cada ficha num site bonito, que a empresa abre no celular e pensa "é isso que eu quero". A prévia é o que fecha a venda, então capricha no visual.

## O que entra: a ficha de cada empresa

As fichas ficam no repositório `mazinho021/projetos`, na branch `claude/jolly-maxwell-l39txo`, em `caca-sites/dados/leads/<slug>.json`. Tem um exemplo em `caca-sites/exemplos/ficha-exemplo.json`. O formato é este:

```json
{
  "slug": "clinica-sorriso-exemplo-cidade-exemplo",
  "nome": "Clínica Sorriso Exemplo",
  "nicho": "odonto",
  "categoria": "Clínica odontológica",
  "telefone": "(19) 99999-0001",
  "whatsapp": "5519999990001",
  "endereco": "Rua Exemplo, 100 - Centro, Cidade Exemplo - SP",
  "bairro": "Centro", "cidade": "Cidade Exemplo", "uf": "SP",
  "lat": -22.9, "lng": -47.06,
  "maps": "https://maps.google.com/?cid=1",
  "nota": 4.8, "avaliacoes": 63,
  "horario": ["segunda-feira: 08:00–18:00", "sábado: 08:00–12:00", "domingo: Fechado"],
  "resumo": "",
  "avaliacoes_destaque": [
    {"autor": "Cliente A", "nota": 5, "texto": "Atendimento excelente...", "quando": "há 2 semanas"}
  ],
  "situacao_site": "sem_site",
  "site_atual": ""
}
```

- Os nichos possíveis são `odonto`, `estetica`, `saude`, `oficina`, `advocacia`, `pet`, `contabil`, `academia`, `imobiliaria`, `servicos`, `restaurante` e `generico`.
- Qualquer campo pode vir vazio: `whatsapp` (quando o telefone é fixo), `horario`, `avaliacoes_destaque`, `resumo`, `bairro`. O site tem que ficar bonito mesmo assim. Por exemplo, sem WhatsApp, o botão vira "Ligar".
- Em `situacao_site: "site_falso"`, o `site_atual` costuma ser o Instagram da empresa. Nesse caso, ponha um link para ele no site.

## O que construir

1. **Um modelo de site por nicho.** Comece por `odonto`, `estetica`, `oficina` e `generico`, e depois faça os outros. Cada modelo tem uma página só, pensada primeiro para o celular, com:
   - topo com o nome da empresa, a categoria e o bairro, mais um botão grande de "Agendar pelo WhatsApp" (`https://wa.me/<whatsapp>`);
   - os serviços típicos do nicho, escritos por você (por exemplo, para odonto: clareamento, implante, ortodontia, limpeza);
   - o selo "⭐ 4,8 · 63 avaliações no Google" e as avaliações em destaque, com o nome do autor e a indicação de que vêm do Google;
   - o horário, o endereço, um mapa ou um botão "Como chegar" com o link `maps`, e o telefone;
   - fotos de banco de imagens com licença livre (Unsplash ou Pexels), que combinem com o nicho. **Não use fotos do Google da empresa**, porque elas têm dono;
   - visual de agência: cada nicho com a sua paleta e a sua tipografia. Não pode parecer um modelo genérico.
2. **Um script gerador.** Ele recebe a pasta de fichas (ou uma ficha só) e gera cada site em `previas/<slug>/index.html`, com o modelo do nicho preenchido. O site precisa ser estático, para publicar de graça.
3. **Avisos de prévia, obrigatórios:**
   - `<meta name="robots" content="noindex, nofollow">` e o cabeçalho `X-Robots-Tag: noindex` no Netlify, para a prévia nunca aparecer no Google como se fosse o site oficial;
   - uma faixa fina e discreta, no topo ou no rodapé: "Prévia de demonstração feita por {vendedor}. Não é o site oficial da {empresa}.", com um botão "Quero este site", que abre o WhatsApp do vendedor com a mensagem "Oi! Vi a prévia da {empresa} e quero saber mais.";
   - o nome e o WhatsApp do vendedor vêm de um arquivo de configuração (`vendedor.nome` e `vendedor.whatsapp`). Por enquanto, use "SEU NOME" e "5500000000000".
4. **Uma imagem de pré-visualização para o WhatsApp (muito importante).** Em cada prévia, gere um `og.jpg` de 1200 × 630 com o print do topo do site e ponha as tags `og:title`, `og:description` e `og:image`. Quando o link é colado no WhatsApp, a empresa vê o próprio site no cartão, antes mesmo de clicar. Faça o print com o Playwright.
5. **Um print do site no celular,** `print-celular.png` com 1080 × 1920, para mandar como imagem na mensagem 3 da sequência.
6. **Uma página de proposta por empresa,** `previas/<slug>/proposta/`, também com `noindex`. Ela tem o print da prévia e três planos lado a lado, com o do meio em destaque:
   - Essencial: R$ 0 de entrada + R$ 79/mês. Site de uma página, domínio e hospedagem;
   - **Profissional (mais escolhido):** R$ 497 + R$ 99/mês. Tudo do Essencial + Google Meu Negócio otimizado, até 5 páginas e formulário;
   - Completo: R$ 997 + R$ 297/mês. Tudo do Profissional + anúncios no Google e relatório mensal (a verba dos anúncios é à parte);
   - depois dos planos, a garantia "no ar em 48 h depois do sinal, ou você não paga", três perguntas frequentes (dá para mudar textos e fotos? o domínio fica no meu nome? posso cancelar?) e o botão "Quero o Profissional", que abre o WhatsApp do vendedor com o plano escrito.
   - Os valores também vêm do arquivo de configuração.
7. **A publicação:** um site só no Netlify para todas as prévias, com cada uma em `https://<site>/<slug>/`. Os slugs não podem se misturar e a raiz do site não lista as empresas: ela mostra uma página neutra.

## O que você me devolve

- O link de cada prévia publicada, numa lista `slug → link`, que eu passo para a sessão do funil com `python3 funil.py previa <slug> <link>`.
- Uma captura da prévia de exemplo no celular (390 px de largura), para eu aprovar o visual antes de gerar todas.
- O comando para gerar e publicar as próximas, como `python3 gerar.py dados/leads/ && netlify deploy --prod`.

Comece pela ficha de exemplo, me mostre o resultado de `odonto` e espere o meu ok antes de fazer os outros nichos.

# WSKZ AI Message Router

Proof of Concept (PoC) opartego na AI systemu kategoryzacji i routingu wiadomości. 
Serwis API przyjmuje zapytania HTTP (`email` + treść wiadomości), które trafiają do AI Agenta 
działającego na lokalnym modelu językowym (Ollama). 
Agent interpretuje treść, klasyfikuje wiadomość do właściwego działu i poprzez
**tool calling** wysyła e-mail do docelowego działu. Wiadomość przechwytywana jest
przez testowy serwer pocztowy (MailHog).

## Uruchomienie

Wymagany jest Docker wraz z obsługą Docker Compose.

```bash
docker compose up -d
```

Polecenie buduje i uruchamia całe środowisko składające się z następujących kontenerów:

| Usługa      | Rola                                                              | Dostęp                        |
|-------------|-------------------------------------------------------------------|-------------------------------|
| `api`       | Serwis API (FastAPI, Python 3.12)                                 | http://localhost:8000         |
| `ollama`    | Lokalny silnik LLM (interfejs OpenAI-compatible pod `/v1`)        | http://localhost:11435        |
| `ollama-init` | Kontener jednorazowy pobierający wagę modelu                    | —                             |
| `mailhog`   | Testowy serwer SMTP + panel webowy                                | http://localhost:8025         |

Podczas pierwszego startu `ollama-init` pobiera domyślny model `qwen3:4b` (wagę można zmienić zmienną
`OLLAMA_MODEL`). Pobrana waga przechowywana jest w wolumenie `ollama_data`, więc jest pobierana tylko raz.
Serwis API startuje dopiero po pomyślnym ukończeniu inicjalizacji modelu. Gotowość środowiska można
zweryfikować pod adresem http://localhost:8000/health.

## Dokumentacja API (Swagger/OpenAPI)

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### Przykładowe zapytanie

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "jan.nowak@example.com",
    "message": "Chciałbym zgłosić urlop na jutro"
  }'
```

## Architektura i podjęte decyzje
- **Pełna konteneryzacja** - każdy komponent działa w osobnym konterze zdefiniowanym w `docker-compose.yml`.
  Dzięki kontenerowi `ollama-init`, który czeka na dostępność Ollamy, pobiera model i później dopiero uruchamia
  serwis API możliwe jest uruchomienie całego środowiska jedynie komendą `docker compose up -d`.
- **Python + FastAPI** - API zaimplementowana w Pythonie, ponieważ mam większe doświadczenie w tym języku, 
  szczególnie w budowaniu API oraz integracji z rozwiązaniami AI. FastAPI zapewnia automatyczną dokumentację
  OpenAPI/Swagger i walidację danych za pomocą Pydantic.
- **Pydantic-ai** - wykorzystany do implementacji AI Agenta oraz obsługi tool/function calling. 
  Upraszcza integrację z modelem Ollama i pozwala agentowi samodzielnie wywoływać zdefiniowane narzędzia.
- **Lokalny LLM (Ollama)** - do analizy używamy lokalnie pobrany model `qwen3:4b`. Wybrałem ten model ze względu na
  dobre wsparcie języka polskiego oraz tool calling. Model `qwen3:8b`nie przyniósł zauważalnej poprawy jakości 
  klasyfikacji, a jego większy rozmiar powodował wyraźnie dłuższy czas podejmowania decyzji. Natomiast modele LLama3.x
  radziły sobie słabiej z językiem polskim.
- **MailHog jako serwer SMTP** - przechwytuje wszystkie wiadomości w środowisku testowym umożliwiając testowanie systemu
  bez wysyłania prawdziwych maili.

## Uwagi

- Kontener `ollama` deklaruje wykorzystanie GPU (NVIDIA). Na maszynach bez dostępnego GPU należy usunąć
  sekcję `ollama.deploy` z `docker-compose.yml` - model będzie wówczas działał na CPU.

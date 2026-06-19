# IoTMeter Extended

Vlastní integrace pro [Home Assistant](https://www.home-assistant.io/) umožňující sledování dat z **IoTMeter** přes lokální síť.

## Funkce

- Monitorování napětí na 3 fázích (U1, U2, U3) ve voltech
- Monitorování proudu na 3 fázích (I1, I2, I3) v ampérech
- Monitorování výkonu (P1, P2, P3, S1, S2, S3) ve wattech
- Monitorování účiníku (F1, F2, F3)
- Podpora EVSE nabíječky pro elektrická vozidla (stav, proud, chyby komunikace)

## Instalace přes HACS

1. Otevřete **HACS** v Home Assistantu
2. Přejděte na **Integrace**
3. Klikněte na ⋮ → **Vlastní repozitáře**
4. Přidejte: `https://github.com/JardaK22/iotmeter_ext` a vyberte typ **Integrace**
5. Vyhledejte **IoTMeter Extended** a klikněte na **Stáhnout**
6. Restartujte Home Assistant

## Instalace starší verze přes HACS

1. HACS → Integrace → IoTMeter Extended
2. Klikněte na ⋮ → **Znovu stáhnout**
3. Vyberte požadovanou verzi ze seznamu

## Konfigurace

1. Nastavení → Zařízení a integrace → **Přidat integraci** → IoTMeter Extended
2. Zadejte **IP adresu** zařízení IoTMeter
3. Zadejte **port** (výchozí: `8000`)

## Verze

| Verze | Popis                                               |
|-------|-----------------------------------------------------|
| 0.5.0 | Počáteční verze s podporou 3-fázového měření a EVSE |
| 0.5.1 | Oprava chyb v sensor.py                             |
| 0.5.5 | Oprava syntaxe                             |
| 0.5.6 | Nejnovější vydání                                   |
| 0.6.0 | Přidány ovládací prvky (switch/number/select/button) |
## Kompatibilita

- Home Assistant 2024.1.0 a novější
- Zařízení IoTMeter s HTTP API

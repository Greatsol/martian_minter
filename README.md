# martian_minter | Dev: [@python_web3](https://t.me/python_web3)
Martian Testnet NFT minter. \
Разработан [@python_web3](https://t.me/python_web3)

## Установка зависимостей
Для работы скрипт нужен [python3.10](https://www.python.org/) или выше.
```bash
pip install -r requirements.txt
```

## Настройка
Файл настройки нужно создать(`cp .env_example .env`) и заполнить:
```
MAIN_PRIVATE_KEY=Приватник от главного кошелька
EXIST_WALLETS=False
WALLETS_AMOUNT=Количество генерируемых кошельков и нфт
TESTNET_URL=https://fullnode.testnet.aptoslabs.com/v1
```

## Запуск
```bash
python run_app.py
```

## Логирование и приватные ключи
Логи пишутся в `log/debug.log`. \
Сгенерированные кошельки хранятся в виде приватных ключей в `private.json`.

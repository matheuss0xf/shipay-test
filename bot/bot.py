# -*- coding: utf-8 -*-
import os, sys, traceback, logging, configparser
import xlsxwriter
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

def main(argv):
    greetings()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    app = Flask(__name__)
    handler = RotatingFileHandler('bot.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # Configure database
    db_url = os.getenv('DATABASE_URL', 'postgresql://shipay:shipay123@127.0.0.1:5432/backend_challenge')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    db = SQLAlchemy(app)

    # Load configuration
    config_path = 'settings/config.ini'
    if not os.path.exists(config_path):
        app.logger.error('Arquivo de configuração não encontrado.')
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    interval_minutes = int(config.get('scheduler', 'IntervalInMinutes', fallback=10))
    app.logger.info(f'Intervalo entre execuções: {interval_minutes} minutos')

    # Schedule tasks
    scheduler = BlockingScheduler()
    scheduler.add_job(task1, 'interval', id='task1_job', minutes=interval_minutes, args=[db])

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

def greetings():
    print('             ##########################')
    print('             # - ACME - Tasks Robot - #')
    print('             # - v 1.0 - 2020-07-28 - #')
    print('             ##########################')

def task1(db):
    file_name = f'data_export_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
    file_path = os.path.join(os.path.curdir, file_name)
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    try:
        orders = db.session.execute('SELECT id, name, email, password, role_id, created_at, updated_at FROM users;')

        worksheet.write_row('A1', ['Id', 'Name', 'Email', 'Password', 'Role Id', 'Created At', 'Updated At'])

        for index, order in enumerate(orders, start=2):
            worksheet.write_row(f'A{index}', order)

        workbook.close()
        print('Job executed successfully!')
    except Exception as e:
        print(f'Erro ao executar tarefa: {e}')
    finally:
        db.session.close()

if __name__ == '__main__':
    main(sys.argv)

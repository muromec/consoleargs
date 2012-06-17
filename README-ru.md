# `сonsoleargs`

В Python есть большое количество библиотек для успешных CLI утилит. Чтение документации и использование эти библиотек создает гнетущее чувство подавленности, меланхолии, мезантропии, суицидальных проявлений и падению потенции. При этом выразительность имеющиеся средства языка все равно оставляют ощущение того что все можно было бы сделать проще. 

Для того чтобы упростить создание утилит коммандной строки мы и сделали библиотеку `consoleargs`. Теперь для того чтобы объявить набор параметров скрипта достаточно функции добавить декоратор. Докстринг функции автоматически становится подсказкой, а параметры функции становятся параметрами скрипта в коммандной строке.

## Примеры использования

Код скрипта `demo.py`:

	from consoleargs import command

	@command
	def main(url, name=None):
	  """
	  :param url: Remote URL 
	  :param name: File name
	  """
	  print """Downloading url '%r' into file '%r'""" % (url, name)

	if __name__ == '__main__':
	  main()

А теперь примеры того как можно вызвать этот скрипт:

	% python demo.py --help
	Usage: demo.py URL [OPTIONS]

	URL:	Remote URL 

	Options:
		--name -n 	File name

	% python demo.py http://www.vurt.ru/
	Downloading url ''http://www.vurt.ru/'' into file 'None'

	% python demo.py http://www.vurt.ru/ --name=index.html
	Downloading url ''http://www.vurt.ru/'' into file ''index.html''

Авторы:

- Илья Петров <https://github.com/muromec>
- Денис Черниенко <https://github.com/DenekUrich>

Документация: 

- Михаил Кашкин <https://github.com/xen>

Ссылки проекта:

- Форкать отсюда <https://github.com/muromec/consoleargs>
- PyPI <http://pypi.python.org/pypi/consoleargs/>
from todoism.extensions import db
from .base import BaseTestCase


class CliTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(CliTestCase, self).setUp()
        db.drop_all()

    def test_init_db(self):
        result = self.runner.invoke(args=['init-db'])
        self.assertIn('正在初始化数据库', result.output)
        self.assertIn('Done!', result.output)

        result = self.runner.invoke(args=['init-db', '--drop'], input='y\n')
        self.assertIn('这将清空整个数据库, 你确定吗', result.output)
        self.assertIn('数据库清理完毕', result.output)
        self.assertIn('Done!', result.output)

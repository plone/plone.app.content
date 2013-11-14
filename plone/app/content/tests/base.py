from Products.PloneTestCase import PloneTestCase as ptc
ptc.setupPloneSite()


class ContentTestCase(ptc.PloneTestCase):
    pass


class ContentFunctionalTestCase(ptc.FunctionalTestCase):
    pass

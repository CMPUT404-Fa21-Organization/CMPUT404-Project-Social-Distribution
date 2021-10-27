import base64
from django.db import models
from django.db.models.deletion import CASCADE
from Author.models import Author

class Base64Field(models.TextField):
    # https://djangosnippets.org/snippets/1669/
    _data = models.TextField(
            db_column='data',
            blank=True)

    def set_data(self, data):
        self._data = base64.b64encode(data)

    def get_data(self):
        return self._data.decode('utf-8')

    data = property(get_data, set_data)

# Create your models here.
class Post(models.Model):
    post_pk = models.CharField(primary_key=True, max_length=100, editable=False)

    author_id = models.ForeignKey(Author, on_delete=CASCADE)
    author = models.JSONField(editable=False)

    id = models.CharField(max_length=200, editable=False)

    type = models.CharField(max_length=30, default='post', editable=False)
    title = models.CharField(max_length=200, editable=True)
    source = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=500, blank=True)

    content_type = (("markdown", "text/markdown"),
                    ("plain", "text/plain"),
                    ("app", "application/base64"),
                    ("png", "image/png;base64"),
                    ("jpeg", "image/jpeg;base64"),
                    ("html", "HTML"),
                    )
    contentType = models.CharField(max_length=20, choices=content_type)

    content = Base64Field()

    post_categories = (
        ('web', 'Web'),
        ('tutorial', 'Tutorial'),
        ('', ''),
    )
    categories = models.CharField(max_length=20, choices=post_categories, editable=False)
    count = models.PositiveBigIntegerField(default=0)
    size = models.PositiveBigIntegerField(default=10)

    comments = models.CharField(max_length=200, editable=False)

    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=20, blank=False, editable=True)
    unlisted = models.BooleanField(blank=False, default=False)

'''
INSERT INTO Posts_post VALUES ("gbeuihfoewh",{"http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072","http://127.0.0.1:8000/","http://127.0.0.1:8000/author/85441b95489243e98b6e87a3d574b072","belton",""}
,"hjhifuhfiishf","post","test","","","","jpeg","dog.jnp", "", "234", "24","comment", "public")
Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan
'''

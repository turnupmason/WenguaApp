"""Show frozen V8 grades with fixed symbolic captions; don't reinterpret scores."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"ios/WenguaAppUI"

class HealthCaptionUserUX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cloud=(UI/"WenguaCloudWelcome.swift").read_text()
        cls.main=(UI/"WenguaDesignPreviewApp.swift").read_text()
        cls.premium=(UI/"WenguaPremiumReadingView.swift").read_text()
        cls.domain=(UI/"WenguaDomainJourneyScreen.swift").read_text()
        cls.history=(UI/"WenguaLocalHistoryView.swift").read_text()
        cls.engine=(UI/"WenguaNativeReadingRouter.swift").read_text()
        cls.template=json.loads((ROOT/"data/templates/health_severity_vnext/reading_template.json").read_text())

    def test_branding_and_no_old_source_or_visible_offline_wording(self):
        self.assertIn("借天地之势，成自己之事",self.cloud)
        self.assertIn("依托二十余部易学古籍的解图体系",self.cloud)
        self.assertIn("历时数年人工搭建核心模型",self.cloud)
        for tag in ["古籍为本","规则推演","东方智慧","决策指引","破局迷茫"]:
            self.assertIn('welcomeTag("'+tag+'")',self.cloud)
        self.assertNotIn("神奇之门",self.cloud)
        self.assertNotIn("开悟之门",self.cloud)
        self.assertNotIn("离线",self.cloud)
        for text in (self.main,self.domain,self.history):
            for line in text.splitlines():
                if 'Text("' in line or 'Button("' in line:
                    self.assertNotIn("离线",line)

    def test_confirm_moment_and_traditional_algorithm_disclaimer(self):
        self.assertIn('Button("确认起局 · 逻辑推演")',self.main)
        self.assertIn("本模型基于古籍规则算法进行推演计算，无人工主观干预，严密还原事情发展之底层逻辑。",self.main)
        self.assertIn("Date().addingTimeInterval(30)",self.main)
        self.assertIn("let finalInstant=Date()",self.main)
        self.assertIn("QIssuePolicy.commitRealCompletedCast(key,validated:true,stored:true)",self.main)

    def test_real_square_palace_and_short_cohost_display(self):
        self.assertIn(".aspectRatio(1,contentMode:.fit)",self.main)
        self.assertIn(".frame(maxWidth:.infinity,alignment:.center)",self.main)
        self.assertIn('identityLabels.joined(separator:"／") + "宫"',self.main)
        self.assertIn('real.heavenStars.map',self.main)
        # Approved Oct 28 single-line 天芮／禽; do not demand the old
        # per-star vertical row generator.
        self.assertIn('(pair.0=="天禽" ? "禽" : pair.0)',self.main)
        self.assertIn('starCarriers.reversed().enumerated()',self.main)
        self.assertIn('QFive.shade(kind,value)',self.main)
        self.assertIn("WenguaPalaceIdentity.labels(nativeReading,palaceID:palace.id)",self.main)
        self.assertIn("if palace.id == 5",self.main)

    def test_pillars_keep_each_element_color(self):
        self.assertIn('QFive.shade("stem",String(stem.prefix(1)))',self.main)
        self.assertIn('QFive.shade("branch",String(stem.suffix(1)))',self.main)
        self.assertIn('QFive.shade("stem",String(value.prefix(1)))',self.main)
        self.assertIn('QFive.shade("branch",String(value.suffix(1)))',self.main)

    def test_all_ten_user_requested_health_grade_captions(self):
        captions={
            "极大吉":("吉局","沉疴顿愈","沉重顽疾迎刃而解，元气彻底恢复"),
            "大吉":("吉局","邪退正复","治疗手段极为对症，病情迅速好转"),
            "中吉":("吉局","身心渐安","病情发展得到控制，正逐步走向康复"),
            "小吉":("吉局","转危为安","虽有波折但无大碍，危险期已经过去"),
            "极小吉":("吉局","正邪相持","虽未根治但病情稳定，需长期精细调养"),
            "极小凶":("凶局","风寒微染","只是皮毛表证小疾，日常多加注意即可"),
            "小凶":("凶局","沉疴隐现","体内已有小病变，切勿拖延需及时就医"),
            "中凶":("凶局","病势缠绵","病情较为顽固反复，治疗过程面临阻力"),
            "大凶":("凶局","元气大伤","病情极其危重凶险，必须全力介入救治"),
            "极大凶":("凶局","命悬一线","运势陷入至暗绝境，急需寻求破局生机")
        }
        for grade,(category,epithet,interpretation) in captions.items():
            with self.subTest(grade=grade):
                self.assertIn('case "'+grade+'"',self.premium)
                self.assertIn('category:"'+category+'"',self.premium)
                self.assertIn('epithet:"'+epithet+'"',self.premium)
                self.assertIn('interpretation:"'+interpretation+'"',self.premium)
        self.assertIn('default: return nil',self.premium)
        self.assertIn('let caption=WenguaHealthGradeCaption.forGrade(grade)',self.premium)
        # The first screen must not collapse to just a grade + one sentence.
        self.assertIn('Text(caption.category)',self.premium)
        self.assertIn('Text(grade+"："+caption.epithet)',self.premium)
        self.assertIn('Text(verdict.frontNarrative(caption))',self.premium)
        self.assertIn('let evidence: String',self.premium)
        self.assertIn('parts.dropLast().joined(separator:',self.premium)
        self.assertNotIn('WenguaNaturalSeveritySummary',self.premium)
        self.assertIn('id == "90_review"',self.premium)
        self.assertIn('id == "91_timing"',self.premium)
        self.assertIn('private let labels = ["专业解卦", "专业解盘"]',self.premium)
        self.assertIn('Text("专 业 解 卦")',self.premium)
        self.assertIn('相关结论仅作为传统文化研究与决策视角参考',self.premium)
        self.assertIn('身体不适请务必及时前往医院就医',self.premium)
        self.assertIn('case "不凶不吉"',self.premium)
        self.assertIn('category:"微恙"',self.premium)
        self.assertIn('epithet:"病势平缓"',self.premium)
        self.assertIn('interpretation:"病情稳定不凶不急，调理即可"',self.premium)
        self.assertIn('综上所述，此病为{grade}。',self.template['macros']['overall_resolved'])

    def test_no_second_engine_and_full_original_reading_untouched(self):
        self.assertNotIn("compute(",self.premium)
        self.assertNotIn("review.score",self.premium)
        self.assertIn('WenguaNativeCustomerView(reading:reading)',self.main)
        self.assertIn('try WenguaNativeReadingRouter.compose(',self.main)
        self.assertIn('rolePalaces:review.roles',self.engine)

if __name__=="__main__":
    unittest.main()

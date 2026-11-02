import SwiftUI

struct WenguaPreparationCard: View {
    let topic: QuestionTopic
    let start: () -> Void
    var body: some View {
        VStack(spacing:24) {
            Image(systemName:"seal").font(.system(size:32,weight:.light))
                .foregroundStyle(Color(red:0.65,green:0.48,blue:0.24))
            Text("准备起局").font(.system(size:30,weight:.semibold,design:.serif))
                .frame(maxWidth:.infinity,alignment:.center)
            VStack(spacing:8) {
                Text("已选定预测方向：").font(.subheadline).foregroundStyle(QStyle.secondary)
                Text(topic.domainTitle+"／"+topic.title)
                    .font(.system(size:20,weight:.semibold,design:.serif))
                    .multilineTextAlignment(.center)
            }
            Divider()
            VStack(alignment:.leading,spacing:16) {
                guidance("普通问事", "直接使用当前时辰起局。")
                guidance("预定事项", "若属于已知、已预定的特定事件，请从本领域「选吉日」进入，按该事项实际发生／约定的时刻起局。")
            }
            Button(action:start) {
                Text(topic.isElective ? "选择预定时辰并填写信息" : "填写问事信息")
                    .font(.headline).frame(maxWidth:.infinity).padding(.vertical,10)
            }.buttonStyle(.borderedProminent).tint(Color(red:0.12,green:0.30,blue:0.31))
            Text("信息填写完毕后，请闭目、端坐，完整静心30秒。确保心平气和、意念集中于所问之事，方可动手起局（无事勿惊，不诚不占）。")
                .font(.subheadline).foregroundStyle(QStyle.secondary).lineSpacing(6)
        }
        .padding(26).frame(maxWidth:.infinity)
        .background(QStyle.surface,in:RoundedRectangle(cornerRadius:24))
    }
    private func guidance(_ title:String,_ text:String) -> some View {
        VStack(alignment:.leading,spacing:5) {
            Text(title+"：").font(.headline)
            Text(text).font(.subheadline).foregroundStyle(QStyle.secondary).lineSpacing(4)
        }.frame(maxWidth:.infinity,alignment:.leading)
    }
}

struct WenguaCivilClockWheel: View {
    @Binding var clock: WenguaScheduledClock
    let timezone: String
    private var firstYear:Int {
        var calendar=Calendar(identifier:.gregorian)
        calendar.timeZone=TimeZone(identifier:timezone) ?? .current
        return min(2150,calendar.component(.year,from:Date()))
    }
    var body: some View {
        HStack(spacing:0) {
            column("年",value:yearBinding,values:Array(firstYear...2150))
            column("月",value:monthBinding,values:Array(1...12))
            column("日",value:$clock.day,values:Array(1...clock.daysInMonth(timezone:timezone)))
            column("时",value:$clock.hour,values:Array(0...23))
            column("分",value:$clock.minute,values:Array(0...59))
        }
    }
    private var yearBinding:Binding<Int> {
        Binding(get:{clock.year},set:{ year in
            var next=clock;next.year=year
            next.day=min(next.day,next.daysInMonth(timezone:timezone));clock=next
        })
    }
    private var monthBinding:Binding<Int> {
        Binding(get:{clock.month},set:{ month in
            var next=clock;next.month=month
            next.day=min(next.day,next.daysInMonth(timezone:timezone));clock=next
        })
    }
    private func column(_ title:String,value:Binding<Int>,values:[Int]) -> some View {
        VStack(spacing:3) {
            Text(title).font(.headline).frame(maxWidth:.infinity)
            Picker(title,selection:value) {
                ForEach(values,id:\.self) { number in Text(String(number)).tag(number) }
            }
            .pickerStyle(.wheel).labelsHidden()
            .frame(maxWidth:.infinity).frame(height:155).clipped()
            .accessibilityLabel(title)
        }.frame(maxWidth:.infinity)
    }
}

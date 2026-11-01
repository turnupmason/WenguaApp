# iOS V8.0 Xcode simulator FAIL

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41339353432
Source SHA: 3155acecdd89d22aab6bb6548bafa507fd9633c5
Result: Xcode/resources/new independent V15 two-clock Swift runtime failed; see preserved logs

Unsigned simulator build is NOT a signed iPhone installation, not an App Store shipment, and not proof of forecast validity.

## Build tail (append-only)
~~~text
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:476:66: error: expected ',' separator
                danger.append(stem+signs.joined(separator:"、")+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:484:78: error: expected ',' separator
                danger.append("天禽携"+bird+signs.joined(separator:"、")+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:450:75: error: '+' is not a postfix unary operator
        let doorsFull="病宫临"+door+"，人物宫临"+patientDoor+"。"+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:451:32: warning: expression of type 'String' is unused
            (doorCross.isEmpty ? "其余门象不另增加主位。" : doorCross+"。")
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:453:81: error: '+' is not a postfix unary operator
        let hourFull="时干"+hourStem+"在"+label(hourPalace)+"宫，与病宫"+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:454:45: error: '+' is not a postfix unary operator
            palaceRelation(hourPalace)+"；"+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:455:53: warning: result of operator '??' is unused
            (hourMatch.map{"其宫亦指"+$0+"。"} ?? "作为事体旁证。")
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:456:69: error: '+' is not a postfix unary operator
        let personFull=relationship+"取用神"+actor.mainStem+"在"+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:457:87: error: '+' is not a postfix unary operator
            label(patientPalace)+"宫，与病宫"+palaceRelation(patientPalace)+"；"+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:458:32: warning: expression of type 'String' is unused
            (actorLine.isEmpty ? "病位仍以天芮所示部位为先。" : actorLine)
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:468:68: error: '+' is not a postfix unary operator
        let formsFull="天芮携"+sky+"加地盘"+illness.earthStem+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:469:60: error: '+' is not a postfix unary operator
            "，见"+formationNames.joined(separator:"、")+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:470:50: warning: result of operator '+' is unused
            "格；合参本宫门神，以"+lead+"为主线。"
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:476:65: error: '+' is not a postfix unary operator
                danger.append(stem+signs.joined(separator:"、")+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:477:55: error: extra argument in call
                    "，传统不利象集中在"+site+"一带")
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:484:77: error: '+' is not a postfix unary operator
                danger.append("天禽携"+bird+signs.joined(separator:"、")+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:485:32: error: extra argument in call
                    "，亦指"+site)
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:159:13: warning: no calls to throwing functions occur within 'try' expression
            try WenguaVNextEngine.factor(kind:kind,symbol:symbol,palace:p.id,
            ^
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift:232:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it
        let macro=try [
        ~~~~^~~~~
        _

Failed frontend command:
/Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-frontend -frontend -emit-module -experimental-skip-non-inlinable-function-bodies-without-types /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPremiumReadingView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaSelectedSignifierGraphV80.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextCustomerComposer.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextReasoner.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextTianrui25.swift -target arm64-apple-ios17.0-simulator -Xllvm -aarch64-use-tbi -enable-objc-interop -sdk /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator18.5.sdk -I /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -F /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -no-color-diagnostics -enable-testing -g -debug-info-format\=dwarf -dwarf-version\=4 -module-cache-path /tmp/wengua-v80-xcode/derived/ModuleCache.noindex -swift-version 5 -enforce-exclusivity\=checked -Onone -D DEBUG -serialize-debugging-options -const-gather-protocols-file /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/WenguaApp_const_extract_protocols.json -enable-experimental-feature DebugDescriptionMacro -enable-bare-slash-regex -empty-abi-descriptor -validate-clang-modules-once -clang-build-session-file /tmp/wengua-v80-xcode/derived/ModuleCache.noindex/Session.modulevalidation -Xcc -working-directory -Xcc /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -resource-dir /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift -enable-anonymous-context-mangled-names -file-compilation-dir /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -Xcc -ivfsstatcache -Xcc /tmp/wengua-v80-xcode/derived/SDKStatCaches.noindex/iphonesimulator18.5-22F76-96ae0914227b19deccb34b33ba7b5dea.sdkstatcache -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/swift-overrides.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-generated-files.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-own-target-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-all-target-headers.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-project-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/include -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources-normal/arm64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources/arm64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources -Xcc -DDEBUG\=1 -module-name 问卦 -frontend-parseable-output -disable-clang-spi -target-sdk-version 18.5 -target-sdk-name iphonesimulator18.5 -external-plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/lib/swift/host/plugins\#/Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/swift-plugin-server -external-plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/local/lib/swift/host/plugins\#/Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/swift-plugin-server -in-process-plugin-server-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/host/libSwiftInProcPluginServer.dylib -plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/host/plugins -plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/local/lib/swift/host/plugins -emit-module-doc-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftdoc -emit-module-source-info-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftsourceinfo -emit-objc-header-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦-Swift.h -serialize-diagnostics-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/WenguaApp-master-emit-module.dia -emit-dependencies-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/WenguaApp-master-emit-module.d -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftmodule -emit-abi-descriptor-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.abi.json
SwiftCompile normal arm64 Compiling\ WenguaCloudWelcome.swift,\ WenguaDesignPreviewApp.swift,\ WenguaDomainJourneyScreen.swift,\ WenguaHealthTemplateBridge.swift,\ WenguaLocalHistoryView.swift,\ WenguaNativeActorBinding.swift,\ WenguaNativeCore.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift (in target 'WenguaApp' from project 'WenguaApp')
SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftEmitModule normal x86_64 Emitting\ module\ for\ 问卦 (in target 'WenguaApp' from project 'WenguaApp')
EmitSwiftModule normal x86_64 (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
Command SwiftCompile failed with a nonzero exit code

** BUILD FAILED **


The following build commands failed:
	EmitSwiftModule normal arm64 (in target 'WenguaApp' from project 'WenguaApp')
	SwiftEmitModule normal arm64 Emitting\ module\ for\ 问卦 (in target 'WenguaApp' from project 'WenguaApp')
	SwiftCompile normal x86_64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
	Building project WenguaApp with scheme WenguaApp and configuration Debug
(4 failures)
~~~

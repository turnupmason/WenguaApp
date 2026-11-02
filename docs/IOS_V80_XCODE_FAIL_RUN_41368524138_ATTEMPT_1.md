# iOS V8.0 Xcode simulator FAIL

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41368524138
Source SHA: bc93c23b2b3752a7019cdaaf4fae5727ba84730f
Result: Xcode/resources/new independent V15 two-clock Swift runtime failed; see preserved logs

Unsigned simulator build is NOT a signed iPhone installation, not an App Store shipment, and not proof of forecast validity.

## Build tail (append-only)
~~~text
SwiftEmitModule normal arm64 Emitting\ module\ for\ 问卦 (in target 'WenguaApp' from project 'WenguaApp')

EmitSwiftModule normal arm64 (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:831:99: error: '+' is not a postfix unary operator
        let conclusion="综上，\(relationship)本次\(conclusionFocus)\(focusRegion)。"+closing+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:832:13: warning: string literal is unused
            "以上为传统病位和症候象意，需以实际检查核实。"
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:903:27: warning: trailing closure in this context is confusable with the body of the statement; pass as a parenthesized argument to silence this warning
              sections.map{$0.id}==required.filter{wanted in
                          ^
                          (      )
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:903:51: warning: trailing closure in this context is confusable with the body of the statement; pass as a parenthesized argument to silence this warning
              sections.map{$0.id}==required.filter{wanted in
                                                  ^
                                                  (
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:168:13: warning: no calls to throwing functions occur within 'try' expression
            try WenguaVNextEngine.factor(kind:kind,symbol:symbol,palace:p.id,
            ^
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift:237:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it
        let macro=try [
        ~~~~^~~~~
        _

SwiftEmitModule normal x86_64 Emitting\ module\ for\ 问卦 (in target 'WenguaApp' from project 'WenguaApp')
Failed frontend command:
/Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-frontend -frontend -emit-module -experimental-skip-non-inlinable-function-bodies-without-types /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPremiumReadingView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaSelectedSignifierGraphV80.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextCustomerComposer.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextReasoner.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextTianrui25.swift -target x86_64-apple-ios17.0-simulator -enable-objc-interop -sdk /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator18.5.sdk -I /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -F /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -no-color-diagnostics -enable-testing -g -debug-info-format\=dwarf -dwarf-version\=4 -module-cache-path /tmp/wengua-v80-xcode/derived/ModuleCache.noindex -swift-version 5 -enforce-exclusivity\=checked -Onone -D DEBUG -serialize-debugging-options -const-gather-protocols-file /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaApp_const_extract_protocols.json -enable-experimental-feature DebugDescriptionMacro -enable-bare-slash-regex -empty-abi-descriptor -validate-clang-modules-once -clang-build-session-file /tmp/wengua-v80-xcode/derived/ModuleCache.noindex/Session.modulevalidation -Xcc -working-directory -Xcc /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -resource-dir /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift -enable-anonymous-context-mangled-names -file-compilation-dir /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -Xcc -ivfsstatcache -Xcc /tmp/wengua-v80-xcode/derived/SDKStatCaches.noindex/iphonesimulator18.5-22F76-96ae0914227b19deccb34b33ba7b5dea.sdkstatcache -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/swift-overrides.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-generated-files.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-own-target-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-all-target-headers.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-project-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/include -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources-normal/x86_64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources/x86_64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources -Xcc -DDEBUG\=1 -module-name 问卦 -frontend-parseable-output -disable-clang-spi -target-sdk-version 18.5 -target-sdk-name iphonesimulator18.5 -external-plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/lib/swift/host/plugins\#/Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/swift-plugin-server -external-plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/local/lib/swift/host/plugins\#/Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/swift-plugin-server -in-process-plugin-server-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/host/libSwiftInProcPluginServer.dylib -plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/host/plugins -plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/local/lib/swift/host/plugins -emit-module-doc-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftdoc -emit-module-source-info-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftsourceinfo -emit-objc-header-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦-Swift.h -serialize-diagnostics-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaApp-master-emit-module.dia -emit-dependencies-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaApp-master-emit-module.d -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftmodule -emit-abi-descriptor-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.abi.json

EmitSwiftModule normal x86_64 (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:831:99: error: '+' is not a postfix unary operator
        let conclusion="综上，\(relationship)本次\(conclusionFocus)\(focusRegion)。"+closing+
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:832:13: warning: string literal is unused
            "以上为传统病位和症候象意，需以实际检查核实。"
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:903:27: warning: trailing closure in this context is confusable with the body of the statement; pass as a parenthesized argument to silence this warning
              sections.map{$0.id}==required.filter{wanted in
                          ^
                          (      )
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:903:51: warning: trailing closure in this context is confusable with the body of the statement; pass as a parenthesized argument to silence this warning
              sections.map{$0.id}==required.filter{wanted in
                                                  ^
                                                  (
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:168:13: warning: no calls to throwing functions occur within 'try' expression
            try WenguaVNextEngine.factor(kind:kind,symbol:symbol,palace:p.id,
            ^
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift:237:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it
        let macro=try [
        ~~~~^~~~~
        _

SwiftCompile normal x86_64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
Command SwiftCompile failed with a nonzero exit code

** BUILD FAILED **


The following build commands failed:
	EmitSwiftModule normal arm64 (in target 'WenguaApp' from project 'WenguaApp')
	SwiftEmitModule normal x86_64 Emitting\ module\ for\ 问卦 (in target 'WenguaApp' from project 'WenguaApp')
	EmitSwiftModule normal x86_64 (in target 'WenguaApp' from project 'WenguaApp')
	SwiftCompile normal arm64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
	Building project WenguaApp with scheme WenguaApp and configuration Debug
(5 failures)
~~~

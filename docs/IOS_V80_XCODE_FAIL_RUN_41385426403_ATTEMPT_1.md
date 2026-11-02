# iOS V8.0 Xcode simulator FAIL

Run: https://github.com/turnupmason/WenguaApp/actions/runs/41385426403
Source SHA: 354b557c156f336866220117d6959809879c9bf5
Result: Xcode/resources/new independent V15 two-clock Swift runtime failed; see preserved logs

Unsigned simulator build is NOT a signed iPhone installation, not an App Store shipment, and not proof of forecast validity.

## Build tail (append-only)
~~~text
SwiftCompile normal x86_64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:348:52: error: '+' is not a postfix unary operator
            let all=(v["qimen_secret_vol13"] ?? [])+
                                                   ^
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:349:23: warning: expression of type '[String]' is unused
                (full ? (v["sanming_viscera"] ?? [])+(v["sanming_body_surface"] ?? []) : [])
                 ~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:1007:27: warning: trailing closure in this context is confusable with the body of the statement; pass as a parenthesized argument to silence this warning
              sections.map{$0.id}==required.filter{wanted in
                          ^
                          (      )
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift:1007:51: warning: trailing closure in this context is confusable with the body of the statement; pass as a parenthesized argument to silence this warning
              sections.map{$0.id}==required.filter{wanted in
                                                  ^
                                                  (

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    
/Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift:237:13: warning: initialization of immutable value 'macro' was never used; consider replacing with assignment to '_' or removing it
        let macro=try [
        ~~~~^~~~~
        _

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

Failed frontend command:
/Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-frontend -frontend -c /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift -primary-file /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift -primary-file /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift -primary-file /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift -primary-file /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift -primary-file /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift -primary-file /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPremiumReadingView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaSelectedSignifierGraphV80.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextCustomerComposer.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextReasoner.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextTianrui25.swift -supplementary-output-file-map /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/supplementaryOutputs-8 -target x86_64-apple-ios17.0-simulator -enable-objc-interop -sdk /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator18.5.sdk -I /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -F /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -no-color-diagnostics -enable-testing -g -debug-info-format\=dwarf -dwarf-version\=4 -module-cache-path /tmp/wengua-v80-xcode/derived/ModuleCache.noindex -swift-version 5 -enforce-exclusivity\=checked -Onone -D DEBUG -serialize-debugging-options -const-gather-protocols-file /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaApp_const_extract_protocols.json -enable-experimental-feature DebugDescriptionMacro -enable-bare-slash-regex -empty-abi-descriptor -validate-clang-modules-once -clang-build-session-file /tmp/wengua-v80-xcode/derived/ModuleCache.noindex/Session.modulevalidation -Xcc -working-directory -Xcc /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -resource-dir /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift -enable-anonymous-context-mangled-names -file-compilation-dir /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -Xcc -ivfsstatcache -Xcc /tmp/wengua-v80-xcode/derived/SDKStatCaches.noindex/iphonesimulator18.5-22F76-96ae0914227b19deccb34b33ba7b5dea.sdkstatcache -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/swift-overrides.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-generated-files.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-own-target-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-all-target-headers.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-project-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/include -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources-normal/x86_64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources/x86_64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources -Xcc -DDEBUG\=1 -module-name 问卦 -frontend-parseable-output -disable-clang-spi -target-sdk-version 18.5 -target-sdk-name iphonesimulator18.5 -external-plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/lib/swift/host/plugins\#/Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/swift-plugin-server -external-plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/local/lib/swift/host/plugins\#/Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/swift-plugin-server -in-process-plugin-server-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/host/libSwiftInProcPluginServer.dylib -plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/host/plugins -plugin-path /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/local/lib/swift/host/plugins -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeCustomerView.o -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeDiscomfortV15.o -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeEnergyBundle.o -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeReadingRouter.o -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeVNextEngine.o -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaPalacePowerDetail.o -index-unit-output-path /WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeCustomerView.o -index-unit-output-path /WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeDiscomfortV15.o -index-unit-output-path /WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeEnergyBundle.o -index-unit-output-path /WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeReadingRouter.o -index-unit-output-path /WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaNativeVNextEngine.o -index-unit-output-path /WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaPalacePowerDetail.o -index-store-path /tmp/wengua-v80-xcode/derived/Index.noindex/DataStore -index-system-modules
SwiftCompile normal x86_64 Compiling\ WenguaPremiumReadingView.swift,\ WenguaPythonVNextVerbatim.swift,\ WenguaSelectedSignifierGraphV80.swift,\ WenguaVNextCustomerComposer.swift,\ WenguaVNextReasoner.swift,\ WenguaVNextTianrui25.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPremiumReadingView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaSelectedSignifierGraphV80.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextCustomerComposer.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextReasoner.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextTianrui25.swift (in target 'WenguaApp' from project 'WenguaApp')
SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPremiumReadingView.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaSelectedSignifierGraphV80.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextCustomerComposer.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextReasoner.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextTianrui25.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftEmitModule normal arm64 Emitting\ module\ for\ 问卦 (in target 'WenguaApp' from project 'WenguaApp')

EmitSwiftModule normal arm64 (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftDriverJobDiscovery normal x86_64 Emitting module for 问卦 (in target 'WenguaApp' from project 'WenguaApp')

SwiftDriver\ Compilation\ Requirements WenguaApp normal x86_64 com.apple.xcode.tools.swift.compiler (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-Swift-Compilation-Requirements -- /Applications/Xcode_16.4.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swiftc -module-name 问卦 -Onone -enforce-exclusivity\=checked @/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.SwiftFileList -DDEBUG -enable-bare-slash-regex -enable-experimental-feature DebugDescriptionMacro -sdk /Applications/Xcode_16.4.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator18.5.sdk -target x86_64-apple-ios17.0-simulator -g -module-cache-path /tmp/wengua-v80-xcode/derived/ModuleCache.noindex -Xfrontend -serialize-debugging-options -enable-testing -index-store-path /tmp/wengua-v80-xcode/derived/Index.noindex/DataStore -swift-version 5 -I /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -F /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator -c -j3 -enable-batch-mode -incremental -Xcc -ivfsstatcache -Xcc /tmp/wengua-v80-xcode/derived/SDKStatCaches.noindex/iphonesimulator18.5-22F76-96ae0914227b19deccb34b33ba7b5dea.sdkstatcache -output-file-map /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaApp-OutputFileMap.json -use-frontend-parseable-output -save-temps -no-color-diagnostics -serialize-diagnostics -emit-dependencies -emit-module -emit-module-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftmodule -validate-clang-modules-once -clang-build-session-file /tmp/wengua-v80-xcode/derived/ModuleCache.noindex/Session.modulevalidation -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/swift-overrides.hmap -emit-const-values -Xfrontend -const-gather-protocols-file -Xfrontend /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/WenguaApp_const_extract_protocols.json -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-generated-files.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-own-target-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-all-target-headers.hmap -Xcc -iquote -Xcc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/问卦-project-headers.hmap -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/include -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources-normal/x86_64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources/x86_64 -Xcc -I/tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources -Xcc -DDEBUG\=1 -emit-objc-header -emit-objc-header-path /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦-Swift.h -working-directory /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI -experimental-emit-module-separately -disable-cmo

** BUILD FAILED **


The following build commands failed:
	SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift (in target 'WenguaApp' from project 'WenguaApp')
	SwiftCompile normal x86_64 Compiling\ WenguaNativeCustomerView.swift,\ WenguaNativeDiscomfortV15.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
	Building project WenguaApp with scheme WenguaApp and configuration Debug
(3 failures)
~~~

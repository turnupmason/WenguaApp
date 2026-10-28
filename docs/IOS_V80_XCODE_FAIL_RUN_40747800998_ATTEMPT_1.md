# iOS V8.0 Xcode simulator FAIL

Run: https://github.com/turnupmason/WenguaApp/actions/runs/40747800998
Source SHA: 8d9357b4e172be66a2db53218007b83c015407a5
Result: Native Xcode SwiftUI build or resource checks failed; see preserved logs

Unsigned simulator build is NOT a signed iPhone installation, not an App Store shipment, and not proof of forecast validity.

## Build tail (append-only)
~~~text
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextCustomerComposer.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextReasoner.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaVNextTianrui25.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftMergeGeneratedHeaders /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources/问卦-Swift.h /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦-Swift.h /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦-Swift.h (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-swiftHeaderTool -arch arm64 /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦-Swift.h -arch x86_64 /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦-Swift.h -o /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/DerivedSources/问卦-Swift.h

SwiftDriverJobDiscovery normal arm64 Compiling WenguaCloudWelcome.swift, WenguaDesignPreviewApp.swift, WenguaDomainJourneyScreen.swift, WenguaHealthTemplateBridge.swift, WenguaLocalHistoryView.swift, WenguaNativeActorBinding.swift (in target 'WenguaApp' from project 'WenguaApp')

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/x86_64-apple-ios-simulator.swiftmodule /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftmodule (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftmodule /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/x86_64-apple-ios-simulator.swiftmodule

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/x86_64-apple-ios-simulator.swiftdoc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftdoc (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftdoc /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/x86_64-apple-ios-simulator.swiftdoc

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/x86_64-apple-ios-simulator.abi.json /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.abi.json (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.abi.json /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/x86_64-apple-ios-simulator.abi.json

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/arm64-apple-ios-simulator.swiftmodule /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftmodule (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftmodule /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/arm64-apple-ios-simulator.swiftmodule

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/arm64-apple-ios-simulator.swiftdoc /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftdoc (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftdoc /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/arm64-apple-ios-simulator.swiftdoc

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/arm64-apple-ios-simulator.abi.json /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.abi.json (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.abi.json /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/arm64-apple-ios-simulator.abi.json

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/Project/x86_64-apple-ios-simulator.swiftsourceinfo /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftsourceinfo (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/x86_64/问卦.swiftsourceinfo /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/Project/x86_64-apple-ios-simulator.swiftsourceinfo

Copy /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/Project/arm64-apple-ios-simulator.swiftsourceinfo /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftsourceinfo (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    builtin-copy -exclude .DS_Store -exclude CVS -exclude .svn -exclude .git -exclude .hg -resolve-src-symlinks -rename /tmp/wengua-v80-xcode/derived/Build/Intermediates.noindex/WenguaApp.build/Debug-iphonesimulator/WenguaApp.build/Objects-normal/arm64/问卦.swiftsourceinfo /tmp/wengua-v80-xcode/derived/Build/Products/Debug-iphonesimulator/问卦.swiftmodule/Project/arm64-apple-ios-simulator.swiftsourceinfo

SwiftCompile normal x86_64 Compiling\ WenguaNativeCore.swift,\ WenguaNativeCustomerView.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
    cd /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI
    

SwiftCompile normal x86_64 Compiling\ WenguaCloudWelcome.swift,\ WenguaDesignPreviewApp.swift,\ WenguaDomainJourneyScreen.swift,\ WenguaHealthTemplateBridge.swift,\ WenguaLocalHistoryView.swift,\ WenguaNativeActorBinding.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift (in target 'WenguaApp' from project 'WenguaApp')
Command SwiftCompile failed with a nonzero exit code

** BUILD FAILED **


The following build commands failed:
	SwiftCompile normal arm64 /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
	SwiftCompile normal arm64 Compiling\ WenguaNativeCore.swift,\ WenguaNativeCustomerView.swift,\ WenguaNativeEnergyBundle.swift,\ WenguaNativeReadingRouter.swift,\ WenguaNativeVNextEngine.swift,\ WenguaPalacePowerDetail.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCore.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeCustomerView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeEnergyBundle.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeReadingRouter.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeVNextEngine.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaPalacePowerDetail.swift (in target 'WenguaApp' from project 'WenguaApp')
	SwiftCompile normal x86_64 Compiling\ WenguaCloudWelcome.swift,\ WenguaDesignPreviewApp.swift,\ WenguaDomainJourneyScreen.swift,\ WenguaHealthTemplateBridge.swift,\ WenguaLocalHistoryView.swift,\ WenguaNativeActorBinding.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaCloudWelcome.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDesignPreviewApp.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaDomainJourneyScreen.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaHealthTemplateBridge.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaLocalHistoryView.swift /Users/runner/work/WenguaApp/WenguaApp/ios/WenguaAppUI/WenguaNativeActorBinding.swift (in target 'WenguaApp' from project 'WenguaApp')
	Building project WenguaApp with scheme WenguaApp and configuration Debug
(4 failures)
~~~

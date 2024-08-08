#!/bin/sh

echo "Sign the excutables"
# find ./dist/scribe_tts_v1_collection -type f -exec codesign --deep --force --options=runtime --entitlements ./entitlements.plist --sign "9B484EA0B09BA52C286D99CF4134AAD45FE03F81" --timestamp {} \;

echo "-- Sign the script file --"
codesign --deep --force --options=runtime --entitlements ./entitlements.plist --sign "9B484EA0B09BA52C286D99CF4134AAD45FE03F81" --timestamp ./dist/scribe_tts_v1_collection/scribe_tts_v1
echo ""
echo "-- Sign the so files --"
codesign --deep --force --options=runtime --entitlements ./entitlements.plist --sign "9B484EA0B09BA52C286D99CF4134AAD45FE03F81" --timestamp ./dist/scribe_tts_v1_collection/_internal/**/*.so

echo ""
echo "-- Sign the dylib files --"
codesign --deep --force --options=runtime --entitlements ./entitlements.plist --sign "9B484EA0B09BA52C286D99CF4134AAD45FE03F81" --timestamp ./dist/scribe_tts_v1_collection/_internal/**/*.dylib


# jects/prismatic/OpenVoice-Scribe/gen_script main* ⇡
# openvoice ❯ mkdir -p dist/Applications/scribe_tts_v1

# ~/Projects/prismatic/OpenVoice-Scribe/gen_script main* ⇡
# openvoice ❯ mv dist/scribe_tts_v1_collection/* dist/Applications/scribe_tts_v1

# worked
# productbuild --identifier "com.reid-prismatic-company.scribe.tts.openvoice.v1.pkg" --sign "104491A3C1079117D63C6AA4AB24A8B49352E035" --timestamp --root dist/Applications/scribe_tts_v1 / scribe_tts_v1.pkg

# didn't work
# xcrun altool --notarize-app --primary-bundle-id "com.reid-prismatic-company.scribe.tts.openvoice.v1.pkg" --username="temphee+kr@gmail.com" --password "@keychain:Developer-altool" --file ./scribe_tts_v1.pkg

# hdiutil create ./scribe_tts_v1.dmg -ov -volname "scribe_tts_v1" -fs HFS+ -srcfolder "./dist"

# xcrun altool --notarize-app --primary-bundle-id "com.reid-prismatic-company.scribe.tts.openvoice.v1" --username temphee+kr@gmail.com --password "ujno-hrwa-espx-zjed" --file ./scribe_tts_v1.dmg


#   xcrun altool --notarization-info "com.reid-prismatic-company.scribe.tts.openvoice.v1" \
#              --username "temphee+kr@gmail.com" \                                    
#              --password "@keychain:Developer-altool"   

# xcrun altool --notarization-history 0 -u "temphee+kr@gmail.com" -p "@keychain:Developer-altool"

# ujno-hrwa-espx-zjed

# hdiutil create ./sribe-tts-v1.dmg -ov -volname "ScribeTTSV1" -fs HFS+ -srcfolder "./dist"

# codesign --verify --deep --verbose=2 ./dist/scribe_tts_v1_collection/scribe_tts_v1
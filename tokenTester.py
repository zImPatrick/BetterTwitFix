import twExtract
import vx_testdata
tokens = ""

tokensList = tokens.split(",")
errorTokens = []
for token in tokensList:
    try:
        twExtract.extractStatusV2(vx_testdata.testNSFWTweet,workaroundTokens=[token])
    except Exception as e:
        print(str(e)+" "+token)
        errorTokens.append(token)
        pass

print("Error tokens: "+str(errorTokens))
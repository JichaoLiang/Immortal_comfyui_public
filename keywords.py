class ContextKeyword:
    Question = "Question"
    DefaultChatAction_history = "DefaultChatAction_history"
    nodewalkcount = "nodewalkcount"
    AutoPass = "AutoPass"
    currentnodeid = "lastnode"
    bgmkey = "BGMusicKey"
    allcustomvalue = "ALL_CUSTOM_VALUE"
    notCustomKeys = [nodewalkcount,AutoPass,currentnodeid,bgmkey]

class EntityKeyword:
    Expression = "Expression"
    CoverImage = "CoverImage"
    MatchCount = "MatchCount"
    NestedIDField = "NestedId"
    ActionKeywordMapping = "ActionKeywordMapping"
    Mapping = "Mapping"
    voiceId = "voiceid"
    Events = "Events"
    ttsspeakerid = "voiceid"
    ttsvoiceseed = "voiceseed"
    data = "Data"
    overridetitle = "TitleOverride"
    settings = "Settings"

class EntitytSettingsKeyword:
    bgmkeysetting = "BGMKeySetting"
    bgmkeyvol = "bgmkeyvol"
    ttsvoicepath = "ttsvoicepath"

    @staticmethod
    def vallist():
        attributes = vars(EntitytSettingsKeyword)
        result = []
        for attribute, value in attributes.items():
            if attribute == "vallist" \
                    or (attribute.startswith("__") and attribute.endswith("__")):
                continue
            result.append(value)
        return result

if __name__ == "__main__":
    print(EntitytSettingsKeyword.vallist())
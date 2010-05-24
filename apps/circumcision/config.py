'''
Created on Apr 8, 2010

@author: Drew Roos
'''

title = "Circumcision"
tab_link = "/circumcision"

incoming_tz = 'Africa/Nairobi'
server_tz = 'America/New_York' #todo: should find a way to set this automatically;
                               #actually not needed at all if scheduler were able to run off UTC
                               #or an arbitrary timezone

notification_days = [1, 2, 3, 4, 5, 6, 7, 8, 14, 21, 28, 35, 41, 42]

default_language = 'en'
itext = {
    'en': {
        'reg-keyword': 'register',
        'reg-success': 'You have been registered. You will receive your notifications at %s',
        'cannot-parse': 'Did not understand; send message as: register [patient id] [desired contact time (HHMM)]',
        'patid-unrecognized': 'Do not recognize patient ID',
        'already-registered': 'You have already been registered. You registered on %s',
        'phone-already-registered': 'This patient ID has already been registered on another phone',
        'patid-already-registered': 'This phone has already been registered for another patient',
        'cannot-parse-time': 'Did not understand contact time; send as HHMM, i.e., 0600 for 6 AM or 2030 for 8:30 PM',
        'intro' : 'If u r not the intended recipient of this Male Circumcision (MC) message, please text STOP to 0722819835 and you will not receive future messages. Thank you.',
        'notif1' : 'This is your MC provider. It is normal to feel a bit of pain and swelling, but if there is severe swelling, bleeding or pain please come back to the clinic. ',
        'notif2' : 'This is your MC provider. Remember do not allow water to soak the dressing before removal on the 3rd day.  ',
        'notif3' : 'Remove the dressing today. Make sure you review the post-op instructions and use the blade provided. Throw away the blade after use.',
        'notif4' : 'This is your MC provider. Always keep the genital area dry n clean to avoid infection. Do not apply any ointment or creams that are not prescribed by the clinic',
        'notif5' : 'This is your MC provider. If you feel heavy pain, swelling, bleeding, or any signs of infection please consult the clinic.',
        'notif6' : "This is your MC provider. Don't forget to come back to the clinic for your day 7 follow-up visit. You will be checked to be certain the healing is going well.",
        'notif7' : 'This is your MC provider. See you at the clinic today for your follow-up visit.',
        'notif8' : 'Good things come to those who wait. Remember no sex or masturbation until the end of 6 weeks.',
        'notif14' : 'This is your MC provider. Be sure to call or come back to the clinic anytime if you have a question or concern.',
        'notif21' : 'This is your MC provider. Abstaining from sex and masturbation ensures that you will heal properly. ',
        'notif28' : 'This is your MC provider. Remember dont have sex until you are fully healed.  ',
        'notif35' : 'Remember that MC does not provide 100% protection from HIV and STIs.',
        'notif41' : 'If you start sex after MC, it is important to protect yourself and your partner by using condoms.',
        'notif42' : 'Remember that MC does not provide 100% protection from HIV and STIs. Be faithful to one partner and use a condom correctly every time you have sex.',
    },
    "luo": {
        'reg-keyword': 'register',
        'reg-success': 'You have been registered. You will receive your notifications at %s',
        'cannot-parse': 'Did not understand; send message as: register [patient id] [desired contact time (HHMM)]',
        'patid-unrecognized': 'Do not recognize patient ID',
        'already-registered': 'You have already been registered. You registered on %s',
        'phone-already-registered': 'This patient ID has already been registered on another phone',
        'patid-already-registered': 'This phone has already been registered for another patient',
        'cannot-parse-time': 'Did not understand contact time; send as HHMM, i.e., 0600 for 6 AM or 2030 for 8:30 PM',
        'intro' : "Ka okin nga't monego yudi mesej mar nyange ni wakwai mondo i or STOP ir namba ni 0722819835 asto ok ibi yudo mesej ni kendo. Ero kamano",
        'notif1' : "ma en joma ne oteri nyange.Winjorem kata kuot matin nyakabedi, to kanitie kuot maokalo,chwer mar remo mang'eny kata rem mathoth to mondo iduog e kar thieth ka",
        'notif2' : 'par ni kik iwe pi donj e bandej.Kapok igole e odiochieng mar adek',
        'notif3' : "Gol bandej kawuono.Ne ni isomo yore mag rito kama ong'adi kendo iti kod wembe mane omiyi.I wit wembe bang tiyogo",
        'notif4' : 'seche duto ket kar duong ni motuo kendo maler mondo kik igam tuo inyalo tudori kod kar thieth.',
        'notif5' : 'Ka iwinjorem mang eny,Kuot chwer mar remo kata ranyisi mar gamo tuo to tudri kod kar thieth.',
        'notif6' : 'Kik wiyi wil maok iduogo e limbe ekar thieth e odiochieng mar abirio7. Ibiro neni mondo ong i ka chango mari dhi maber',
        'notif7' : 'Ma en joma ne oteri nyange.Wanere e kar thieth kawuono ka ibiro elimbe',
        'notif8' : 'Gik mabeyo biro ne jok marito.Par ni onge bedo e achiel kata puo ruok  nyaka bang jumbe',
        'notif14' : 'Ma en joma ne oteri nyange.Bed gi chir mar go simo kata duogo e kar thieth e samoro amora ma in kod penjo kata wach machandi',
        'notif21' : 'Ma en joma ne oteri nyange. Weyo ma ok I bedo e achiel kata puo ruok  biro miyo ichango maber',
        'notif28' : 'ma en joma ne oteri nyange.par ni,kik ibad e achiel nyaka ichang maber',
        'notif35' : 'Par ni nyange ok geng yudo kute mag ayaki kata touche mag nyeje gi atamalo 100%   ',
        'notif41' : 'sama idok e bedo e achiel bang nyange,ber mondo iritri kod jaherani kuom tiyo kod kondom',
        'notif42' : 'par ninyange ok geng yudo kute mag ayaki kata nyae gi atamalo 100.Chomri kad jaherani achiel kenda iti kod kondom kaka  owinjore eseche duto ma I bedo e achiel',
    }, 
    "sw": {
        'reg-keyword': 'register',
        'reg-success': 'You have been registered. You will receive your notifications at %s',
        'cannot-parse': 'Did not understand; send message as: register [patient id] [desired contact time (HHMM)]',
        'patid-unrecognized': 'Do not recognize patient ID',
        'already-registered': 'You have already been registered. You registered on %s',
        'phone-already-registered': 'This patient ID has already been registered on another phone',
        'patid-already-registered': 'This phone has already been registered for another patient',
        'cannot-parse-time': 'Did not understand contact time; send as HHMM, i.e., 0600 for 6 AM or 2030 for 8:30 PM',
        'intro' : 'Kama wewe sio mwenye kupokea ujumbe huu wa kupashwa tohara tafadhali tuma ujumbe  STOP kwa 0722819835 na hautapata ujumbe huu tena. Asante',
        'notif1' : 'Huyu ni yule aliyekutoza tohara.  Ni kawaida kusikia uchungu kidogo na uvimbe lakini kama kuna uvumbe zaidi kutoka damu au uchungu tafadhali rudi katika kliniki',
        'notif2' : 'Huyu ni yule aliyekutoza tohara. Kumbuka kutowacha maji kulowa alfafa kabla ya kuitoa siku ya tatu',
        'notif3' : 'Toa alfafa leo.  Hakikisha kurudia maelezo uliyopewa baada ya kutahiriwa na tumia uwembe uliyopewa. Tupa wembe baada ya kutumia.',
        'notif4' : 'Huyu ni yule aliyekutoza tohara Kila wakati wacha sehemu yako ya siri ikiwa kavu na safi kuzuia magonjwa  Usipake dawa yeyote ambayo hukuandikiwa katika Kliniki',
        'notif5' : 'Huyu ni yule aliyekutoza tohara. Ukisikia uchungu zaidi, uvimbe, kutokwa damu au dalili yeyote ya uambukizo tafadhali kuja Kliniki',
        'notif6' : 'Huyu ni yule aliyekutoza tohara. Usisahau kurudi kwenye Kliniki kwa maelezo zaidi baada ya siku saba.  Utaangaliwa kuhakikisha kuwa kupona kunaendelea.',
        'notif7' : 'Huyu ni yule aliyekutoza tohara.  Tuonanae katika Kliniki leo kwa maelezo na kuonekana ya kufuatia',
        'notif8' : 'Vitu vizuri huja kwa wale ambao hungoja, kumbuka kutofanya mapenzi au kujichua hadi baada ya wiki sita',
        'notif14' : 'Huyu ni yule aliyekutoza tohara.  Hakikisha kuwa unapiga simu au kurudi kwenye Kliniki wakati wowote una maswali au tashuishi',
        'notif21' : 'Huyu ni yule aliyekutoza tohara.  Kujiepusha kutokana na ngono na kujichua inakuhakikishia uponyaji kamili. ',
        'notif28' : 'Huyu ni yule aliyekutoza tohara.  Kumbuka, usifanye mapenzi  hadi upone kabisa',
        'notif35' : 'Kumbuka kutahiri haikupi kinga 100% kutokana na ugonjwa wa ukimwi na zina',
        'notif41' : 'Ukisha aanza kufanya mapenzi tena baada ya kutahiriwa, ni muhimu kujikinga na mpenzi wako kwa kutimia mipira sahihi, kila wakati ukifanya mapenzi ',
        'notif42' : 'Kumbuka kutahiri haikupi kinga 100% kutokana na ukimwi na zinaa Kuwa mwaminifu kwa mpenzi moja na utumie mpira kwa usahihi kila wakati unapofanya mapenzi',
    }
}

from api.models import *


class DowngradeProfile:
    def downgrade(self, upgrade_profile, user):
        ###################DOWNGRADE PROFILE##############
        print('::::::::::::SHOWING DOWNGRADE::::::::::::')
        upgrade_profile.plan = Plans.objects.get(id=3)
        upgrade_profile.expire_at = None
        upgrade_profile.subscriptionId = None
        upgrade_profile.refId = None
        upgrade_profile.save()
        # UpgradeProfile.objects.get(id=upgrade_profile.id).update(plan=Plans.objects.get(id=3))

        ##############DEACTIVE HIS TEAM MEMBERS########
        User.objects.filter(invited_by=user.id).update(is_active=False)

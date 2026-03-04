import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Tabs, TabPanel, Spinner, Button, Toggle, Slider } from '@/components/ui';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { StatusDot } from '@/components/ui';
import * as settingsService from '@/services/settingsService';
import { ROLE_PERMISSIONS, ROLE_LABELS } from '@/constants';
import type { EscalationRule, ConfidenceThresholds, RetentionPolicy, ExclusionZone, UserRole } from '@/types';

export function SettingsPage() {
  const [tab, setTab] = useState('escalation');
  const [escalationRules, setEscalationRules] = useState<EscalationRule[]>([]);
  const [thresholds, setThresholds] = useState<ConfidenceThresholds>({ highMin: 85, mediumMin: 60, lowMin: 30 });
  const [retention, setRetention] = useState<RetentionPolicy>({ clipRetentionDays: 7, metadataRetentionDays: 90, autoPurgeEnabled: true, purgeThresholdPercent: 90 });
  const [exclusionZones, setExclusionZones] = useState<ExclusionZone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [rules, t, r, zones] = await Promise.all([
        settingsService.getEscalationRules(),
        settingsService.getConfidenceThresholds(),
        settingsService.getRetentionPolicy(),
        settingsService.getExclusionZones(),
      ]);
      setEscalationRules(rules);
      setThresholds(t);
      setRetention(r);
      setExclusionZones(zones);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader title="Settings" subtitle="System configuration" />

      <Tabs
        tabs={[
          { id: 'escalation', label: 'Escalation Rules' },
          { id: 'confidence', label: 'Confidence Thresholds' },
          { id: 'retention', label: 'Retention' },
          { id: 'exclusion', label: 'Exclusion Zones' },
          { id: 'roles', label: 'Roles & Permissions' },
        ]}
        activeTab={tab}
        onChange={setTab}
      />

      <TabPanel id="escalation" activeTab={tab}>
        <Card>
          <CardContent>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Delay</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Target</TableHead>
                  <TableHead>Enabled</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {escalationRules.map(rule => (
                  <TableRow key={rule.id}>
                    <TableCell>{rule.delayMinutes} min</TableCell>
                    <TableCell className="uppercase text-xs">{rule.action}</TableCell>
                    <TableCell>{rule.target}</TableCell>
                    <TableCell>
                      <Toggle
                        checked={rule.enabled}
                        onChange={(checked) => {
                          const updated = { ...rule, enabled: checked };
                          settingsService.updateEscalationRule(updated);
                          setEscalationRules(prev => prev.map(r => r.id === rule.id ? updated : r));
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel id="confidence" activeTab={tab}>
        <Card>
          <CardContent className="space-y-6">
            <Slider label="High Confidence Minimum" value={thresholds.highMin} min={50} max={100} onChange={v => setThresholds(prev => ({ ...prev, highMin: v }))} />
            <Slider label="Medium Confidence Minimum" value={thresholds.mediumMin} min={30} max={80} onChange={v => setThresholds(prev => ({ ...prev, mediumMin: v }))} />
            <Slider label="Low Confidence Minimum" value={thresholds.lowMin} min={10} max={60} onChange={v => setThresholds(prev => ({ ...prev, lowMin: v }))} />
            <Button onClick={() => settingsService.updateConfidenceThresholds(thresholds)}>Save Thresholds</Button>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel id="retention" activeTab={tab}>
        <Card>
          <CardContent className="space-y-6">
            <Slider label="Clip Retention (days)" value={retention.clipRetentionDays} min={3} max={14} onChange={v => setRetention(prev => ({ ...prev, clipRetentionDays: v }))} />
            <Slider label="Metadata Retention (days)" value={retention.metadataRetentionDays} min={30} max={365} step={30} onChange={v => setRetention(prev => ({ ...prev, metadataRetentionDays: v }))} />
            <Toggle label="Auto-purge enabled" checked={retention.autoPurgeEnabled} onChange={v => setRetention(prev => ({ ...prev, autoPurgeEnabled: v }))} />
            {retention.autoPurgeEnabled && (
              <Slider label="Auto-purge threshold (%)" value={retention.purgeThresholdPercent} min={70} max={95} onChange={v => setRetention(prev => ({ ...prev, purgeThresholdPercent: v }))} />
            )}
            <Button onClick={() => settingsService.updateRetentionPolicy(retention)}>Save Retention Policy</Button>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel id="exclusion" activeTab={tab}>
        <Card>
          <CardContent>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Room</TableHead>
                  <TableHead>Zone</TableHead>
                  <TableHead>Enabled</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {exclusionZones.map(zone => (
                  <TableRow key={zone.id}>
                    <TableCell className="font-medium">{zone.roomNumber}</TableCell>
                    <TableCell>{zone.zoneName}</TableCell>
                    <TableCell>
                      <Toggle
                        checked={zone.enabled}
                        onChange={(checked) => {
                          const updated = { ...zone, enabled: checked };
                          settingsService.updateExclusionZone(updated);
                          setExclusionZones(prev => prev.map(z => z.id === zone.id ? updated : z));
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel id="roles" activeTab={tab}>
        <Card>
          <CardContent>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Role</TableHead>
                  <TableHead>Permissions</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {(Object.keys(ROLE_LABELS) as UserRole[]).map(role => (
                  <TableRow key={role}>
                    <TableCell className="font-medium">{ROLE_LABELS[role]}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {ROLE_PERMISSIONS[role].map(p => (
                          <span key={p} className="inline-flex px-1.5 py-0.5 text-[10px] bg-gray-100 text-gray-600 rounded">
                            {p}
                          </span>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabPanel>
    </div>
  );
}

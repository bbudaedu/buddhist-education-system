// Database service would be used for actual statistics queries
// import { databaseService } from './databaseService';
import { healthMonitoringService } from './healthMonitoringService';
import { getSchedulerInstance } from './dailySchedulerService';

/**
 * Subscription statistics interface
 */
export interface SubscriptionStats {
  totalSubscribers: number;
  activeSubscribers: number;
  newSubscribersToday: number;
  newSubscribersThisWeek: number;
  newSubscribersThisMonth: number;
  subscriptionTrends: SubscriptionTrend[];
}

/**
 * Subscription trend data point
 */
export interface SubscriptionTrend {
  date: string;
  newSubscriptions: number;
  unsubscriptions: number;
  totalActive: number;
}

/**
 * Delivery statistics interface
 */
export interface DeliveryStats {
  totalNotificationsSent: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  deliverySuccessRate: number;
  averageDeliveryTime: number;
  recentDeliveries: RecentDelivery[];
  errorBreakdown: ErrorBreakdown[];
}

/**
 * Recent delivery information
 */
export interface RecentDelivery {
  date: string;
  totalRecipients: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  booksProcessed: number;
  processingDuration: number;
}

/**
 * Error breakdown by type
 */
export interface ErrorBreakdown {
  errorType: string;
  count: number;
  percentage: number;
  description: string;
}

/**
 * System status overview
 */
export interface SystemStatusOverview {
  overallHealth: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  lastProcessingTime?: Date | undefined;
  nextScheduledTime?: Date | undefined;
  activeServices: string[];
  criticalIssues: string[];
  warnings: string[];
}

/**
 * Manual trigger result
 */
export interface ManualTriggerResult {
  success: boolean;
  message: string;
  executionId?: string;
  startTime: Date;
  estimatedDuration?: number;
}

/**
 * Administrative dashboard service for system monitoring and management
 */
export class AdminDashboardService {
  private static instance: AdminDashboardService;
  private auditLog: AuditLogEntry[] = [];

  private constructor() {}

  /**
   * Get singleton instance
   */
  public static getInstance(): AdminDashboardService {
    if (!AdminDashboardService.instance) {
      AdminDashboardService.instance = new AdminDashboardService();
    }
    return AdminDashboardService.instance;
  }

  /**
   * Get subscription statistics
   */
  public async getSubscriptionStats(): Promise<SubscriptionStats> {
    try {
      // Import subscription service dynamically to avoid circular dependencies
      const { subscriptionService } = await import('./subscriptionService');
      
      // Get all subscribed users
      const subscribedUsers = await subscriptionService.getSubscribedUsers();
      
      // Calculate statistics
      const totalSubscribers = subscribedUsers.length;
      const activeSubscribers = subscribedUsers.filter(user => user.isSubscribed).length;
      
      // Calculate new subscribers today
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const newSubscribersToday = subscribedUsers.filter(user => {
        const subDate = new Date(user.subscriptionDate);
        subDate.setHours(0, 0, 0, 0);
        return subDate.getTime() === today.getTime();
      }).length;

      // Calculate new subscribers this week
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      const newSubscribersThisWeek = subscribedUsers.filter(user => 
        new Date(user.subscriptionDate) >= weekAgo
      ).length;

      // Calculate new subscribers this month
      const monthAgo = new Date();
      monthAgo.setMonth(monthAgo.getMonth() - 1);
      const newSubscribersThisMonth = subscribedUsers.filter(user => 
        new Date(user.subscriptionDate) >= monthAgo
      ).length;

      const stats: SubscriptionStats = {
        totalSubscribers,
        activeSubscribers,
        newSubscribersToday,
        newSubscribersThisWeek,
        newSubscribersThisMonth,
        subscriptionTrends: [] // TODO: Implement trend calculation if needed
      };

      this.logAuditEvent('subscription_stats_viewed', 'System', 'Subscription statistics accessed');
      
      return stats;
    } catch (error) {
      console.error('Failed to get subscription stats:', error);
      throw new Error('Failed to retrieve subscription statistics');
    }
  }

  /**
   * Get delivery statistics
   */
  public async getDeliveryStats(): Promise<DeliveryStats> {
    try {
      // Import subscription service dynamically to avoid circular dependencies
      const { subscriptionService } = await import('./subscriptionService');
      
      // Get delivery statistics from subscription service
      const deliveryMetrics = await subscriptionService.getDeliveryMetrics();
      
      const stats: DeliveryStats = {
        totalNotificationsSent: deliveryMetrics.totalNotifications,
        successfulDeliveries: deliveryMetrics.successfulDeliveries,
        failedDeliveries: deliveryMetrics.failedDeliveries,
        deliverySuccessRate: deliveryMetrics.successRate,
        averageDeliveryTime: deliveryMetrics.averageProcessingTime,
        recentDeliveries: deliveryMetrics.recentDeliveries.map(delivery => ({
          date: delivery.processingDate.toISOString().split('T')[0],
          totalRecipients: delivery.totalRecipients,
          successfulDeliveries: delivery.successfulDeliveries,
          failedDeliveries: delivery.failedDeliveries,
          booksProcessed: delivery.booksProcessed,
          processingDuration: delivery.processingDurationSeconds || 0
        } as RecentDelivery)),
        errorBreakdown: [] // TODO: Implement error breakdown if needed
      };

      this.logAuditEvent('delivery_stats_viewed', 'System', 'Delivery statistics accessed');
      
      return stats;
    } catch (error) {
      console.error('Failed to get delivery stats:', error);
      
      // Return empty stats if there's an error
      const emptyStats: DeliveryStats = {
        totalNotificationsSent: 0,
        successfulDeliveries: 0,
        failedDeliveries: 0,
        deliverySuccessRate: 0,
        averageDeliveryTime: 0,
        recentDeliveries: [],
        errorBreakdown: []
      };
      
      return emptyStats;
    }
  }

  /**
   * Get system status overview
   */
  public async getSystemStatusOverview(): Promise<SystemStatusOverview> {
    try {
      const healthStatus = await healthMonitoringService.performHealthCheck();
      const scheduler = getSchedulerInstance();
      const schedulerStatus = scheduler.getStatus();

      const activeServices: string[] = [];
      const criticalIssues: string[] = [];
      const warnings: string[] = [];

      // Analyze service health
      Object.entries(healthStatus.services).forEach(([serviceName, service]) => {
        if (service.status === 'healthy') {
          activeServices.push(serviceName);
        } else if (service.status === 'unhealthy') {
          criticalIssues.push(`${serviceName}: ${service.error || 'Service unhealthy'}`);
        } else if (service.status === 'degraded') {
          warnings.push(`${serviceName}: Service degraded`);
        }
      });

      // Check scheduler status
      if (schedulerStatus.isRunning) {
        activeServices.push('scheduler');
      } else {
        warnings.push('Scheduler is not running');
      }

      const overview: SystemStatusOverview = {
        overallHealth: healthStatus.status,
        uptime: healthStatus.metrics.uptime,
        lastProcessingTime: undefined, // Would need to be tracked separately
        nextScheduledTime: schedulerStatus.nextExecution ? new Date(schedulerStatus.nextExecution) : undefined,
        activeServices,
        criticalIssues,
        warnings
      };

      this.logAuditEvent('system_status_viewed', 'System', 'System status overview accessed');
      
      return overview;
    } catch (error) {
      console.error('Failed to get system status:', error);
      throw new Error('Failed to retrieve system status');
    }
  }

  /**
   * Trigger manual notification processing
   */
  public async triggerManualNotification(triggeredBy: string = 'Admin', testData?: any): Promise<ManualTriggerResult> {
    try {
      const startTime = new Date();
      
      this.logAuditEvent('manual_trigger_initiated', triggeredBy, 'Manual notification processing triggered');
      
      const scheduler = getSchedulerInstance();
      
      let result;
      if (testData) {
        // 使用測試資料進行通知
        result = await scheduler.processTestData(testData);
      } else {
        // 正常的手動觸發
        result = await scheduler.manualTrigger();
      }
      
      const triggerResult: ManualTriggerResult = {
        success: result.success,
        message: result.success ? 'Manual trigger completed successfully' : (result.errorMessage || 'Manual trigger failed'),
        executionId: `manual_${Date.now()}`,
        startTime,
        estimatedDuration: result.processingTime
      };

      this.logAuditEvent(
        'manual_trigger_completed', 
        triggeredBy, 
        `Manual trigger ${result.success ? 'succeeded' : 'failed'}: ${result.errorMessage || 'No error message'}`
      );
      
      return triggerResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      this.logAuditEvent('manual_trigger_failed', 'System', `Manual trigger failed: ${errorMessage}`);
      
      return {
        success: false,
        message: `Manual trigger failed: ${errorMessage}`,
        startTime: new Date()
      };
    }
  }

  /**
   * Get audit log entries
   */
  public getAuditLog(limit: number = 50): AuditLogEntry[] {
    return this.auditLog
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  /**
   * Clear old audit log entries
   */
  public clearOldAuditEntries(daysOld: number = 30): number {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysOld);
    
    const initialLength = this.auditLog.length;
    this.auditLog = this.auditLog.filter(entry => entry.timestamp > cutoffDate);
    
    const removedCount = initialLength - this.auditLog.length;
    
    if (removedCount > 0) {
      this.logAuditEvent('audit_cleanup', 'System', `Removed ${removedCount} old audit entries`);
    }
    
    return removedCount;
  }

  /**
   * Get system performance summary
   */
  public async getPerformanceSummary(): Promise<PerformanceSummary> {
    try {
      const healthStatus = await healthMonitoringService.performHealthCheck();
      const memoryMB = Math.round(healthStatus.metrics.memoryUsage.heapUsed / 1024 / 1024);
      const uptimeHours = Math.round(healthStatus.metrics.uptime / 3600);

      return {
        memoryUsageMB: memoryMB,
        uptimeHours,
        healthScore: this.calculateHealthScore(healthStatus),
        lastHealthCheck: healthStatus.timestamp,
        criticalAlerts: healthStatus.services.database.status === 'unhealthy' ? 1 : 0
      };
    } catch (error) {
      console.error('Failed to get performance summary:', error);
      throw new Error('Failed to retrieve performance summary');
    }
  }

  /**
   * Log audit event
   */
  private logAuditEvent(action: string, user: string, details: string): void {
    const entry: AuditLogEntry = {
      id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      action,
      user,
      details,
      ipAddress: 'localhost', // In a real implementation, this would come from the request
      userAgent: 'AdminDashboardService'
    };

    this.auditLog.push(entry);
    
    // Keep only the last 1000 entries to prevent memory issues
    if (this.auditLog.length > 1000) {
      this.auditLog = this.auditLog.slice(-1000);
    }

    console.log(`[AUDIT] ${entry.timestamp.toISOString()} - ${user}: ${action} - ${details}`);
  }

  /**
   * Calculate health score based on system status
   */
  private calculateHealthScore(healthStatus: any): number {
    const services = Object.values(healthStatus.services);
    const healthyCount = services.filter((s: any) => s.status === 'healthy').length;
    const totalServices = services.length;
    
    return Math.round((healthyCount / totalServices) * 100);
  }
}

/**
 * Audit log entry interface
 */
export interface AuditLogEntry {
  id: string;
  timestamp: Date;
  action: string;
  user: string;
  details: string;
  ipAddress: string;
  userAgent: string;
}

/**
 * Performance summary interface
 */
export interface PerformanceSummary {
  memoryUsageMB: number;
  uptimeHours: number;
  healthScore: number;
  lastHealthCheck: Date;
  criticalAlerts: number;
}

// Export singleton instance
export const adminDashboardService = AdminDashboardService.getInstance();
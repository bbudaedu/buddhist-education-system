import { databaseService } from './databaseService';
import { config } from '../config';
import { promises as fs } from 'fs';

/**
 * System health status interface
 */
export interface SystemHealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: Date;
  services: {
    database: ServiceHealth;
    scheduler: ServiceHealth;
    notification: ServiceHealth;
    fileSystem: ServiceHealth;
  };
  metrics: SystemMetrics;
}

/**
 * Individual service health interface
 */
export interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  responseTime?: number;
  lastCheck: Date;
  error?: string;
  details?: Record<string, any>;
}

/**
 * System performance metrics interface
 */
export interface SystemMetrics {
  uptime: number;
  memoryUsage: NodeJS.MemoryUsage;
  cpuUsage?: number;
  activeConnections?: number;
  processingStats: ProcessingStats;
}

/**
 * Processing statistics interface
 */
export interface ProcessingStats {
  totalNotificationsSent: number;
  totalSubscribers: number;
  lastProcessingTime?: Date | undefined;
  averageProcessingDuration?: number | undefined;
  errorRate: number;
}

/**
 * Health monitoring service for system status and metrics
 */
export class HealthMonitoringService {
  private static instance: HealthMonitoringService;
  private healthCheckInterval?: NodeJS.Timeout | undefined;
  private lastHealthCheck?: SystemHealthStatus;
  private processingStats: ProcessingStats = {
    totalNotificationsSent: 0,
    totalSubscribers: 0,
    errorRate: 0,
    lastProcessingTime: undefined,
    averageProcessingDuration: undefined
  };

  private constructor() {}

  /**
   * Get singleton instance
   */
  public static getInstance(): HealthMonitoringService {
    if (!HealthMonitoringService.instance) {
      HealthMonitoringService.instance = new HealthMonitoringService();
    }
    return HealthMonitoringService.instance;
  }

  /**
   * Start periodic health monitoring
   */
  public startMonitoring(intervalMs: number = 60000): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = setInterval(async () => {
      try {
        await this.performHealthCheck();
      } catch (error) {
        console.error('Health check failed:', error);
      }
    }, intervalMs);

    console.log(`Health monitoring started with ${intervalMs}ms interval`);
  }

  /**
   * Stop health monitoring
   */
  public stopMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = undefined;
      console.log('Health monitoring stopped');
    }
  }

  /**
   * Perform comprehensive health check
   */
  public async performHealthCheck(): Promise<SystemHealthStatus> {
    const startTime = Date.now();
    
    try {
      const [
        databaseHealth,
        schedulerHealth,
        notificationHealth,
        fileSystemHealth
      ] = await Promise.all([
        this.checkDatabaseHealth(),
        this.checkSchedulerHealth(),
        this.checkNotificationHealth(),
        this.checkFileSystemHealth()
      ]);

      const metrics = await this.collectSystemMetrics();
      
      // Determine overall system status
      const services = {
        database: databaseHealth,
        scheduler: schedulerHealth,
        notification: notificationHealth,
        fileSystem: fileSystemHealth
      };

      const overallStatus = this.determineOverallStatus(services);

      const healthStatus: SystemHealthStatus = {
        status: overallStatus,
        timestamp: new Date(),
        services,
        metrics
      };

      this.lastHealthCheck = healthStatus;
      
      // Log health status
      this.logHealthStatus(healthStatus, Date.now() - startTime);
      
      return healthStatus;
    } catch (error) {
      console.error('Health check error:', error);
      
      const errorHealthStatus: SystemHealthStatus = {
        status: 'unhealthy',
        timestamp: new Date(),
        services: {
          database: { status: 'unhealthy', lastCheck: new Date(), error: 'Health check failed' },
          scheduler: { status: 'unhealthy', lastCheck: new Date(), error: 'Health check failed' },
          notification: { status: 'unhealthy', lastCheck: new Date(), error: 'Health check failed' },
          fileSystem: { status: 'unhealthy', lastCheck: new Date(), error: 'Health check failed' }
        },
        metrics: {
          uptime: process.uptime(),
          memoryUsage: process.memoryUsage(),
          processingStats: this.processingStats
        }
      };

      this.lastHealthCheck = errorHealthStatus;
      return errorHealthStatus;
    }
  }

  /**
   * Get last health check result
   */
  public getLastHealthCheck(): SystemHealthStatus | undefined {
    return this.lastHealthCheck;
  }

  /**
   * Check database connectivity and performance
   */
  private async checkDatabaseHealth(): Promise<ServiceHealth> {
    const startTime = Date.now();
    
    try {
      // Test basic connectivity
      const isConnected = await databaseService.testConnection();
      
      if (!isConnected) {
        return {
          status: 'unhealthy',
          lastCheck: new Date(),
          error: 'Database connection failed'
        };
      }

      // Test query performance
      const queryStartTime = Date.now();
      await databaseService.searchBooks('test', 1);
      const queryTime = Date.now() - queryStartTime;

      const responseTime = Date.now() - startTime;
      
      // Determine status based on response time
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      if (responseTime > 5000) {
        status = 'unhealthy';
      } else if (responseTime > 2000) {
        status = 'degraded';
      }

      return {
        status,
        responseTime,
        lastCheck: new Date(),
        details: {
          queryTime,
          connectionPoolActive: true
        }
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
        error: error instanceof Error ? error.message : 'Unknown database error'
      };
    }
  }

  /**
   * Check scheduler service health
   */
  private async checkSchedulerHealth(): Promise<ServiceHealth> {
    try {
      // Check if scheduler is enabled
      if (!config.scheduler.enabled) {
        return {
          status: 'degraded',
          lastCheck: new Date(),
          details: {
            enabled: false,
            reason: 'Scheduler is disabled in configuration'
          }
        };
      }

      // Check scheduler configuration
      const configValid = this.validateSchedulerConfig();
      
      if (!configValid) {
        return {
          status: 'unhealthy',
          lastCheck: new Date(),
          error: 'Invalid scheduler configuration'
        };
      }

      return {
        status: 'healthy',
        lastCheck: new Date(),
        details: {
          enabled: true,
          nextExecution: this.getNextScheduledExecution(),
          configuration: {
            dailyTime: config.scheduler.dailyExecutionTime,
            maxRetries: config.scheduler.maxRetries
          }
        }
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        lastCheck: new Date(),
        error: error instanceof Error ? error.message : 'Unknown scheduler error'
      };
    }
  }

  /**
   * Check notification system health
   */
  private async checkNotificationHealth(): Promise<ServiceHealth> {
    try {
      // Check notification configuration
      const configValid = this.validateNotificationConfig();
      
      if (!configValid) {
        return {
          status: 'unhealthy',
          lastCheck: new Date(),
          error: 'Invalid notification configuration'
        };
      }

      // Check LINE API connectivity (basic check)
      const lineApiHealthy = await this.checkLineApiHealth();
      
      if (!lineApiHealthy) {
        return {
          status: 'degraded',
          lastCheck: new Date(),
          error: 'LINE API connectivity issues'
        };
      }

      return {
        status: 'healthy',
        lastCheck: new Date(),
        details: {
          configuration: {
            maxRecipientsPerBatch: config.notifications.maxRecipientsPerBatch,
            enableRichMessages: config.notifications.enableRichMessages
          },
          lineApiStatus: 'connected'
        }
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        lastCheck: new Date(),
        error: error instanceof Error ? error.message : 'Unknown notification error'
      };
    }
  }

  /**
   * Check file system health for ebook integration
   */
  private async checkFileSystemHealth(): Promise<ServiceHealth> {
    try {
      // Check if ebook processor path exists
      const ebookProcessorExists = await this.checkFileExists(config.scheduler.ebookProcessorPath);
      
      // Check if output directory is accessible
      const outputDirAccessible = await this.checkDirectoryAccess(config.scheduler.outputDataPath);
      
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      const issues: string[] = [];
      
      if (!ebookProcessorExists) {
        status = 'degraded';
        issues.push('Ebook processor not found');
      }
      
      if (!outputDirAccessible) {
        status = 'degraded';
        issues.push('Output directory not accessible');
      }

      return {
        status,
        lastCheck: new Date(),
        details: {
          ebookProcessorPath: config.scheduler.ebookProcessorPath,
          ebookProcessorExists,
          outputDataPath: config.scheduler.outputDataPath,
          outputDirAccessible,
          issues: issues.length > 0 ? issues : undefined
        }
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        lastCheck: new Date(),
        error: error instanceof Error ? error.message : 'Unknown file system error'
      };
    }
  }

  /**
   * Collect system performance metrics
   */
  private async collectSystemMetrics(): Promise<SystemMetrics> {
    const memoryUsage = process.memoryUsage();
    const uptime = process.uptime();
    
    // Update processing stats from database
    await this.updateProcessingStats();
    
    return {
      uptime,
      memoryUsage,
      processingStats: this.processingStats
    };
  }

  /**
   * Update processing statistics from database
   */
  private async updateProcessingStats(): Promise<void> {
    try {
      // This would typically query the notification_logs and user_subscriptions tables
      // For now, we'll use placeholder values since the tables might not exist yet
      this.processingStats = {
        totalNotificationsSent: 0, // Would query from notification_logs
        totalSubscribers: 0, // Would query from user_subscriptions
        errorRate: 0, // Would calculate from delivery_failures
        lastProcessingTime: undefined, // Would get from latest notification_logs entry
        averageProcessingDuration: undefined // Would calculate from notification_logs
      };
    } catch (error) {
      console.error('Failed to update processing stats:', error);
    }
  }

  /**
   * Determine overall system status based on individual services
   */
  private determineOverallStatus(services: Record<string, ServiceHealth>): 'healthy' | 'degraded' | 'unhealthy' {
    const statuses = Object.values(services).map(service => service.status);
    
    if (statuses.includes('unhealthy')) {
      return 'unhealthy';
    }
    
    if (statuses.includes('degraded')) {
      return 'degraded';
    }
    
    return 'healthy';
  }

  /**
   * Validate scheduler configuration
   */
  private validateSchedulerConfig(): boolean {
    try {
      const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
      return timeRegex.test(config.scheduler.dailyExecutionTime) &&
             config.scheduler.maxRetries >= 0 &&
             config.scheduler.retryDelayMinutes > 0;
    } catch {
      return false;
    }
  }

  /**
   * Validate notification configuration
   */
  private validateNotificationConfig(): boolean {
    try {
      return config.notifications.maxRecipientsPerBatch > 0 &&
             config.notifications.deliveryTimeoutMs > 0 &&
             config.notifications.maxBooksPerMessage > 0;
    } catch {
      return false;
    }
  }

  /**
   * Check LINE API health (basic connectivity)
   */
  private async checkLineApiHealth(): Promise<boolean> {
    try {
      // This is a basic check - in a real implementation, you might
      // make a simple API call to verify connectivity
      return !!(config.line.channelAccessToken && config.line.channelSecret);
    } catch {
      return false;
    }
  }

  /**
   * Check if file exists
   */
  private async checkFileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check directory access
   */
  private async checkDirectoryAccess(dirPath: string): Promise<boolean> {
    try {
      await fs.access(dirPath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get next scheduled execution time
   */
  private getNextScheduledExecution(): Date {
    const now = new Date();
    const timeParts = config.scheduler.dailyExecutionTime.split(':');
    const hours = parseInt(timeParts[0] || '0', 10);
    const minutes = parseInt(timeParts[1] || '0', 10);
    
    const nextExecution = new Date(now);
    nextExecution.setHours(hours, minutes, 0, 0);
    
    // If the time has already passed today, schedule for tomorrow
    if (nextExecution <= now) {
      nextExecution.setDate(nextExecution.getDate() + 1);
    }
    
    return nextExecution;
  }

  /**
   * Log health status
   */
  private logHealthStatus(healthStatus: SystemHealthStatus, checkDuration: number): void {
    const statusEmoji = {
      healthy: '✅',
      degraded: '⚠️',
      unhealthy: '❌'
    };

    console.log(`${statusEmoji[healthStatus.status]} System Health Check (${checkDuration}ms)`);
    console.log(`Overall Status: ${healthStatus.status.toUpperCase()}`);
    
    Object.entries(healthStatus.services).forEach(([serviceName, service]) => {
      const serviceEmoji = statusEmoji[service.status];
      const responseTime = (service.responseTime !== undefined) ? ` (${service.responseTime}ms)` : '';
      console.log(`  ${serviceEmoji} ${serviceName}: ${service.status}${responseTime}`);
      
      if (service.error) {
        console.log(`    Error: ${service.error}`);
      }
    });

    // Log memory usage if significant
    const memoryMB = Math.round(healthStatus.metrics.memoryUsage.heapUsed / 1024 / 1024);
    if (memoryMB > 100) {
      console.log(`📊 Memory Usage: ${memoryMB}MB`);
    }
  }

  /**
   * Update processing statistics (called by other services)
   */
  public updateStats(stats: Partial<ProcessingStats>): void {
    this.processingStats = { ...this.processingStats, ...stats };
  }
}

// Export singleton instance
export const healthMonitoringService = HealthMonitoringService.getInstance();